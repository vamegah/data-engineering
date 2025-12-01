#!/usr/bin/env python3
"""
Automated Reporting System
Generates PDF reports and sends email alerts for financial analysis

"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import sys
import os

from sqlalchemy import DECIMAL

sys.path.append(os.path.join(os.path.dirname(__file__), "../../shared"))

from shared.config.database import DatabaseConfig
from shared.utils.helpers import setup_plotting
import warnings

warnings.filterwarnings("ignore")


class FinancialReporter:
    def __init__(self):
        self.engine = DatabaseConfig.get_engine()
        setup_plotting()

    def generate_market_summary(self):
        """Generate market summary for report"""
        try:
            # Get latest market data
            query = """
            SELECT 
                s.symbol,
                s.company_name,
                s.sector,
                sp.close as latest_price,
                sp.date
            FROM stocks s
            JOIN stock_prices sp ON s.stock_id = sp.stock_id
            WHERE sp.date = (SELECT MAX(date) FROM stock_prices WHERE stock_id = s.stock_id)
            ORDER BY sp.close DESC
            LIMIT 20
            """

            market_data = pd.read_sql(query, self.engine)

            # Calculate daily returns
            returns_query = """
            SELECT 
                s.symbol,
                AVG(dr.daily_return_pct) as avg_daily_return,
                STDDEV(dr.daily_return_pct) as volatility
            FROM daily_returns dr
            JOIN stocks s ON dr.stock_id = s.stock_id
            WHERE dr.date >= CURRENT_DATE - INTERVAL '30 days'
            GROUP BY s.symbol
            """

            returns_data = pd.read_sql(returns_query, self.engine)

            # Merge data
            summary_data = market_data.merge(returns_data, on="symbol", how="left")

            return summary_data
        except Exception as e:
            print(f"Error generating market summary: {e}")
            return pd.DataFrame()

    def create_report_visualizations(self, output_path="../reports/"):
        """Create visualizations for the report"""
        os.makedirs(output_path, exist_ok=True)

        try:
            # Get data for visualizations
            prices_df = pd.read_sql("SELECT * FROM stock_prices", self.engine)
            stocks_df = pd.read_sql("SELECT * FROM stocks", self.engine)

            prices_df["date"] = pd.to_datetime(prices_df["date"])

            # Create multiple visualizations
            fig, axes = plt.subplots(2, 2, figsize=(15, 12))

            # 1. Price trend for top 5 stocks
            top_stocks = prices_df.groupby("stock_id")["close"].last().nlargest(5).index
            for stock_id in top_stocks:
                stock_data = prices_df[prices_df["stock_id"] == stock_id]
                stock_name = stocks_df[stocks_df["stock_id"] == stock_id][
                    "symbol"
                ].iloc[0]
                axes[0, 0].plot(
                    stock_data["date"],
                    stock_data["close"],
                    label=stock_name,
                    linewidth=2,
                )

            axes[0, 0].set_title("Top 5 Stocks - Price Trends")
            axes[0, 0].set_xlabel("Date")
            axes[0, 0].set_ylabel("Price")
            axes[0, 0].legend()
            axes[0, 0].tick_params(axis="x", rotation=45)

            # 2. Sector performance
            sector_data = prices_df.merge(stocks_df, on="stock_id")
            sector_performance = (
                sector_data.groupby(["sector", "date"])["close"].mean().reset_index()
            )
            latest_sector = (
                sector_performance.groupby("sector")["close"]
                .last()
                .sort_values(ascending=False)
            )
            axes[0, 1].barh(range(len(latest_sector)), latest_sector.values)
            axes[0, 1].set_yticks(range(len(latest_sector)))
            axes[0, 1].set_yticklabels(latest_sector.index)
            axes[0, 1].set_title("Sector Performance (Latest Prices)")
            axes[0, 1].set_xlabel("Average Price")

            # 3. Volume analysis
            volume_data = prices_df.groupby("date")["volume"].sum().tail(30)
            axes[1, 0].plot(
                volume_data.index, volume_data.values, color="orange", linewidth=2
            )
            axes[1, 0].set_title("Market Trading Volume (Last 30 Days)")
            axes[1, 0].set_xlabel("Date")
            axes[1, 0].set_ylabel("Volume")
            axes[1, 0].tick_params(axis="x", rotation=45)

            # 4. Returns distribution
            returns_data = pd.read_sql(
                "SELECT daily_return_pct FROM daily_returns WHERE date >= CURRENT_DATE - INTERVAL '90 days'",
                self.engine,
            )
            axes[1, 1].hist(
                returns_data["daily_return_pct"], bins=50, alpha=0.7, edgecolor="black"
            )
            axes[1, 1].set_title("Daily Returns Distribution")
            axes[1, 1].set_xlabel("Daily Return (%)")
            axes[1, 1].set_ylabel("Frequency")

            plt.tight_layout()
            plt.savefig(f"{output_path}market_report.png", dpi=300, bbox_inches="tight")
            plt.close()

            return True

        except Exception as e:
            print(f"Error creating visualizations: {e}")
            return False

    def generate_pdf_report(self, output_path="../reports/financial_report.pdf"):
        """Generate PDF report using reportlab"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import (
                SimpleDocTemplate,
                Paragraph,
                Spacer,
                Table,
                TableStyle,
                Image,
            )
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            from reportlab.lib.units import inch

            # Create PDF document
            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            # Title
            title_style = ParagraphStyle(
                "CustomTitle",
                parent=styles["Heading1"],
                fontSize=24,
                spaceAfter=30,
                textColor=colors.navy,
            )

            story.append(Paragraph("Financial Market Analysis Report", title_style))
            story.append(
                Paragraph(
                    f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}",
                    styles["Normal"],
                )
            )
            story.append(Spacer(1, 20))

            # Market Summary
            market_data = self.generate_market_summary()

            if not market_data.empty:
                story.append(Paragraph("Market Summary", styles["Heading2"]))

                # Key metrics
                total_stocks = len(market_data)
                avg_price = market_data["latest_price"].mean()
                top_performer = market_data.nlargest(1, "latest_price").iloc[0]

                summary_text = f"""
                Total Stocks Tracked: {total_stocks}<br/>
                Average Stock Price: ${avg_price:.2f}<br/>
                Highest Priced Stock: {top_performer['symbol']} (${top_performer['latest_price']:.2f})<br/>
                Report Period: Last 30 Days<br/>
                """

                story.append(Paragraph(summary_text, styles["Normal"]))
                story.append(Spacer(1, 20))

                # Top performers table
                story.append(Paragraph("Top Performing Stocks", styles["Heading3"]))

                table_data = [
                    ["Symbol", "Company", "Sector", "Price", "Avg Return", "Volatility"]
                ]
                for _, row in market_data.head(10).iterrows():
                    table_data.append(
                        [
                            row["symbol"],
                            (
                                row["company_name"][:20] + "..."
                                if len(row["company_name"]) > 20
                                else row["company_name"]
                            ),
                            row["sector"],
                            f"${row['latest_price']:.2f}",
                            (
                                f"{row['avg_daily_return']:.2f}%"
                                if pd.notna(row["avg_daily_return"])
                                else "N/A"
                            ),
                            (
                                f"{row['volatility']:.2f}%"
                                if pd.notna(row["volatility"])
                                else "N/A"
                            ),
                        ]
                    )

                table = Table(
                    table_data,
                    colWidths=[
                        0.8 * inch,
                        1.5 * inch,
                        1.2 * inch,
                        0.8 * inch,
                        1 * inch,
                        1 * inch,
                    ],
                )
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                            ("FONTSIZE", (0, 0), (-1, 0), 10),
                            ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                            ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                            ("FONTSIZE", (0, 1), (-1, -1), 8),
                            ("GRID", (0, 0), (-1, -1), 1, colors.black),
                        ]
                    )
                )

                story.append(table)
                story.append(Spacer(1, 20))

            # Add visualization
            if self.create_report_visualizations():
                story.append(Paragraph("Market Visualizations", styles["Heading2"]))
                img = Image(
                    "../reports/market_report.png", width=6 * inch, height=4 * inch
                )
                story.append(img)

            # Recommendations
            story.append(
                Paragraph("Key Insights & Recommendations", styles["Heading2"])
            )

            insights = """
            <b>Market Insights:</b><br/>
            • Monitor high-volatility stocks for trading opportunities<br/>
            • Consider sector diversification based on performance trends<br/>
            • Watch for unusual volume patterns that may indicate market moves<br/>
            • Review daily returns distribution for risk assessment<br/>
            <br/>
            <b>Recommended Actions:</b><br/>
            • Rebalance portfolio based on sector performance<br/>
            • Set stop-loss orders for high-volatility positions<br/>
            • Monitor economic indicators for market direction<br/>
            • Review position sizes based on risk tolerance<br/>
            """

            story.append(Paragraph(insights, styles["Normal"]))
            story.append(Spacer(1, 20))
            # Build PDF
            doc.build(story)
            print(f"✅ PDF report generated: {output_path}")
            return True

        except Exception as e:
            print(f"❌ Error generating PDF report: {e}")
            return False

    def send_email(self, recipient, subject, body, attachment_path=None):
        """Send email with report attachment"""
        try:
            # Email configuration from environment variables
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            port = int(os.getenv("SMTP_PORT", "587"))
            sender_email = os.getenv("SENDER_EMAIL")
            password = os.getenv("EMAIL_PASSWORD")

            if not sender_email or not password:
                print(
                    "⚠️ Email credentials not configured. Set SENDER_EMAIL and EMAIL_PASSWORD environment variables."
                )
                return False

            # Create message
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = recipient
            msg["Subject"] = subject

            # Add body
            msg.attach(MIMEText(body, "html"))

            # Add attachment
            if attachment_path and os.path.exists(attachment_path):
                with open(attachment_path, "rb") as attachment:
                    part = MIMEBase("application", "octet-stream")
                    part.set_payload(attachment.read())

                encoders.encode_base64(part)
                part.add_header(
                    "Content-Disposition",
                    f"attachment; filename= {os.path.basename(attachment_path)}",
                )
                msg.attach(part)

            # Send email
            server = smtplib.SMTP(smtp_server, port)
            server.starttls()
            server.login(sender_email, password)
            text = msg.as_string()
            server.sendmail(sender_email, recipient, text)
            server.quit()

            print(f"✅ Email sent to {recipient}")
            return True
        except Exception as e:
            print(f"❌ Error sending email: {e}")
            return False

    def generate_daily_report(self):
        """Generate and send daily report"""
        print("📊 Generating daily financial report...")

        # Generate PDF report
        report_path = "../reports/daily_financial_report.pdf"
        success = self.generate_pdf_report(report_path)

        if success:
            # Prepare email content
            current_date = datetime.now().strftime("%Y-%m-%d")
            subject = f"Daily Financial Market Report - {current_date}"

            body = f"""
            <html>
            <body>
            <h2>Daily Financial Market Report</h2>
            <p>Date: {current_date}</p>
            <p>Your daily financial market analysis report is attached.</p>
            <p>This report includes:</p>
            <ul>
            <li>Market summary and key metrics</li>
            <li>Top performing stocks analysis</li>
            <li>Sector performance trends</li>
            <li>Market visualizations and charts</li>
            <li>Investment recommendations</li>
            </ul>
            <p>Best regards,<br/>Financial Analysis System</p>
            </body>
            </html>
            """

            # Send email (uncomment and configure to actually send)
            # self.send_email_alert(
            #     recipient="investor@example.com",
            #     subject=subject,
            #     body=body,
            #     attachment_path=report_path
            # )

            print("✅ Daily report generation completed!")
            print(
                "💡 Configure email settings in automated_reporting.py to enable email alerts"
            )

        return success


def main():
    """Main function for automated reporting"""
    reporter = FinancialReporter()

    # Generate daily report
    reporter.generate_daily_report()
    print("\n🚀 Automated reporting system ready!")
    print("Next steps:")
    print("1. Configure email settings in the send_email_alert method")
    print("2. Set up cron job for daily execution")
    print("3. Customize report content based on your needs")


if __name__ == "__main__":
    main()
