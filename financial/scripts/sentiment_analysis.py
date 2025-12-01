#!/usr/bin/env python3
"""
Financial News Sentiment Analysis
Analyzes news sentiment and correlates with stock performance
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import requests
import json
import sys
import os

from sympy import python
import yaml
sys.path.append(os.path.join(os.path.dirname(__file__), '../../shared'))

from shared.config.database import DatabaseConfig
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import warnings
warnings.filterwarnings('ignore')

class FinancialSentimentAnalyzer:
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.engine = DatabaseConfig.get_engine()
        
    def get_sample_news(self):
        """Get sample financial news (in real scenario, use NewsAPI or similar)"""
        # Sample financial news headlines
        news_data = [
            {
                'headline': 'Federal Reserve announces interest rate hike to combat inflation',
                'date': datetime(2023, 1, 1),
                'source': 'Financial Times',
                'stock_symbol': 'SPY'
            },
            {
                'headline': 'Tech stocks rally as earnings exceed expectations',
                'date': datetime(2023, 1, 2),
                'source': 'Bloomberg',
                'stock_symbol': 'AAPL'
            },
            {
                'headline': 'Market volatility increases amid geopolitical tensions',
                'date': datetime(2023, 1, 3),
                'source': 'Reuters',
                'stock_symbol': 'VIX'
            },
            {
                'headline': 'Apple reports record quarterly revenue driven by iPhone sales',
                'date': datetime(2023, 1, 4),
                'source': 'CNBC',
                'stock_symbol': 'AAPL'
            },
            {
                'headline': 'Oil prices surge as OPEC announces production cuts',
                'date': datetime(2023, 1, 5),
                'source': 'Wall Street Journal',
                'stock_symbol': 'XOM'
            },
            {
                'headline': 'Bank stocks decline amid regulatory concerns',
                'date': datetime(2023, 1, 6),
                'source': 'Financial Times',
                'stock_symbol': 'JPM'
            },
            {
                'headline': 'Tesla deliveries beat estimates, shares jump 8%',
                'date': datetime(2023, 1, 7),
                'source': 'MarketWatch',
                'stock_symbol': 'TSLA'
            },
            {
                'headline': 'Amazon Web Services continues strong cloud growth',
                'date': datetime(2023, 1, 8),
                'source': 'TechCrunch',
                'stock_symbol': 'AMZN'
            },
            {
                'headline': 'Inflation data comes in lower than expected',
                'date': datetime(2023, 1, 9),
                'source': 'Reuters',
                'stock_symbol': 'SPY'
            },
            {
                'headline': 'Microsoft announces major AI partnership',
                'date': datetime(2023, 1, 10),
                'source': 'Business Insider',
                'stock_symbol': 'MSFT'
            }
        ]
        
        return pd.DataFrame(news_data)
    
    def analyze_sentiment_textblob(self, text):
        """Analyze sentiment using TextBlob"""
        analysis = TextBlob(text)
        return analysis.sentiment.polarity
    
    def analyze_sentiment_vader(self, text):
        """Analyze sentiment using VADER"""
        scores = self.analyzer.polarity_scores(text)
        return scores
    
    def get_sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score >= 0.05:
            return 'Positive'
        elif score <= -0.05:
            return 'Negative'
        else:
            return 'Neutral'
    
    def analyze_news_sentiment(self, news_df):
        """Perform comprehensive sentiment analysis on news"""
        print("📰 Analyzing news sentiment...")
        
        results = []
        
        for _, news in news_df.iterrows():
            # Analyze with both methods
            textblob_score = self.analyze_sentiment_textblob(news['headline'])
            vader_scores = self.analyze_sentiment_vader(news['headline'])
            
            # Use VADER compound score as primary (better for financial text)
            sentiment_score = vader_scores['compound']
            sentiment_label = self.get_sentiment_label(sentiment_score)
            
            results.append({
                'headline': news['headline'],
                'date': news['date'],
                'source': news['source'],
                'stock_symbol': news['stock_symbol'],
                'sentiment_score': sentiment_score,
                'sentiment_label': sentiment_label,
                'textblob_score': textblob_score,
                'vader_positive': vader_scores['pos'],
                'vader_negative': vader_scores['neg'],
                'vader_neutral': vader_scores['neu']
            })
        
        return pd.DataFrame(results)
    
    def correlate_sentiment_with_returns(self, sentiment_df, prices_df):
        """Correlate news sentiment with stock returns"""
        print("🔗 Correlating sentiment with stock performance...")
        
        # Merge sentiment with price data
        merged_data = []
        
        for symbol in sentiment_df['stock_symbol'].unique():
            symbol_sentiment = sentiment_df[sentiment_df['stock_symbol'] == symbol]
            symbol_prices = prices_df[prices_df['symbol'] == symbol]
            
            for _, news in symbol_sentiment.iterrows():
                news_date = news['date']
                
                # Find price data around news date
                price_data = symbol_prices[
                    (symbol_prices['date'] >= news_date - timedelta(days=2)) &
                    (symbol_prices['date'] <= news_date + timedelta(days=2))
                ]
                
                if len(price_data) >= 2:
                    # Calculate return around news
                    price_before = price_data[price_data['date'] < news_date]['close'].iloc[-1] if len(price_data[price_data['date'] < news_date]) > 0 else None
                    price_after = price_data[price_data['date'] > news_date]['close'].iloc[0] if len(price_data[price_data['date'] > news_date]) > 0 else None
                    
                    if price_before and price_after:
                        return_1day = (price_after - price_before) / price_before * 100
                        
                        merged_data.append({
                            'symbol': symbol,
                            'headline': news['headline'],
                            'date': news_date,
                            'sentiment_score': news['sentiment_score'],
                            'sentiment_label': news['sentiment_label'],
                            'return_1day': return_1day,
                            'abs_return': abs(return_1day)
                        })
        
        return pd.DataFrame(merged_data)
    
    def generate_sentiment_report(self, sentiment_df, correlation_df):
        """Generate comprehensive sentiment analysis report"""
        print("📊 Generating sentiment analysis report...")
        
        # Sentiment distribution
        sentiment_dist = sentiment_df['sentiment_label'].value_counts()
        
        # Average sentiment by stock
        avg_sentiment_by_stock = sentiment_df.groupby('stock_symbol')['sentiment_score'].mean().sort_values(ascending=False)
        
        # Correlation analysis
        if not correlation_df.empty:
            correlation = correlation_df['sentiment_score'].corr(correlation_df['return_1day'])
            positive_news_avg_return = correlation_df[correlation_df['sentiment_score'] > 0]['return_1day'].mean()
            negative_news_avg_return = correlation_df[correlation_df['sentiment_score'] < 0]['return_1day'].mean()
        else:
            correlation = 0
            positive_news_avg_return = 0
            negative_news_avg_return = 0
        
        # Create visualizations
        self.create_sentiment_visualizations(sentiment_df, correlation_df)
        
        return {
            'total_news_articles': len(sentiment_df),
            'sentiment_distribution': sentiment_dist,
            'average_sentiment_score': sentiment_df['sentiment_score'].mean(),
            'most_positive_stock': avg_sentiment_by_stock.index[0] if len(avg_sentiment_by_stock) > 0 else 'N/A',
            'most_negative_stock': avg_sentiment_by_stock.index[-1] if len(avg_sentiment_by_stock) > 0 else 'N/A',
            'sentiment_return_correlation': correlation,
            'positive_news_avg_return': positive_news_avg_return,
            'negative_news_avg_return': negative_news_avg_return
        }
    
    def create_sentiment_visualizations(self, sentiment_df, correlation_df):
        """Create sentiment analysis visualizations"""
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # Sentiment distribution
        sentiment_counts = sentiment_df['sentiment_label'].value_counts()
        axes[0,0].pie(sentiment_counts.values, labels=sentiment_counts.index, autopct='%1.1f%%', startangle=90)
        axes[0,0].set_title('News Sentiment Distribution')
        
        # Sentiment by stock
        stock_sentiment = sentiment_df.groupby('stock_symbol')['sentiment_score'].mean().sort_values()
        axes[0,1].barh(range(len(stock_sentiment)), stock_sentiment.values)
        axes[0,1].set_yticks(range(len(stock_sentiment)))
        axes[0,1].set_yticklabels(stock_sentiment.index)
        axes[0,1].set_title('Average Sentiment Score by Stock')
        axes[0,1].set_xlabel('Sentiment Score')
        
        # Sentiment over time
        sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
        daily_sentiment = sentiment_df.groupby('date')['sentiment_score'].mean()
        axes[1,0].plot(daily_sentiment.index, daily_sentiment.values, marker='o')
        axes[1,0].set_title('Daily Average Sentiment Score')
        axes[1,0].set_xlabel('Date')
        axes[1,0].set_ylabel('Sentiment Score')
        axes[1,0].tick_params(axis='x', rotation=45)
        
        # Sentiment vs Returns scatter
        if not correlation_df.empty:
            axes[1,1].scatter(correlation_df['sentiment_score'], correlation_df['return_1day'], alpha=0.6)
            axes[1,1].axhline(y=0, color='red', linestyle='--', alpha=0.5)
            axes[1,1].axvline(x=0, color='red', linestyle='--', alpha=0.5)
            axes[1,1].set_xlabel('Sentiment Score')
            axes[1,1].set_ylabel('1-Day Return (%)')
            axes[1,1].set_title('Sentiment vs Stock Returns')

        plt.tight_layout()
        plt.savefig('../data/processed/sentiment_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
    
    def run_complete_analysis(self):
        """Run complete sentiment analysis pipeline"""
        print("🚀 Starting Financial Sentiment Analysis...")
        
        # Get sample news data
        news_df = self.get_sample_news()
        
        # Analyze sentiment
        sentiment_df = self.analyze_news_sentiment(news_df)
        
        # Load price data for correlation
        try:
            prices_df = pd.read_sql("SELECT * FROM stock_prices_real_time", self.engine)
            prices_df['date'] = pd.to_datetime(prices_df['date'])
        except:
            prices_df = pd.read_csv('../data/raw/prices_real_time.csv')
            prices_df['date'] = pd.to_datetime(prices_df['date'])
        
        # Correlate with returns
        correlation_df = self.correlate_sentiment_with_returns(sentiment_df, prices_df)

        # Generate report
        report = self.generate_sentiment_report(sentiment_df, correlation_df)
        
        # Save results
        sentiment_df.to_csv('../data/processed/news_sentiment.csv', index=False)
        correlation_df.to_csv('../data/processed/sentiment_correlation.csv', index=False)
        
        print("\n📈 SENTIMENT ANALYSIS REPORT")
        print("=" * 50)
        print(f"Total articles analyzed: {report['total_news_articles']}")
        print(f"Average sentiment score: {report['average_sentiment_score']:.3f}")
        print(f"Most positive stock: {report['most_positive_stock']}")
        print(f"Most negative stock: {report['most_negative_stock']}")
        print(f"Sentiment-Return correlation: {report['sentiment_return_correlation']:.3f}")
        print(f"Positive news avg return: {report['positive_news_avg_return']:.2f}%")
        print(f"Negative news avg return: {report['negative_news_avg_return']:.2f}%")
        
        print("\n✅ Sentiment analysis completed!")
        
        return sentiment_df, correlation_df

def main():
    """Main function for sentiment analysis"""
    analyzer = FinancialSentimentAnalyzer()
    sentiment_df, correlation_df = analyzer.run_complete_analysis()

    # Display sample results
    print("\n📰 Sample Sentiment Analysis:")
    print(sentiment_df[['headline', 'sentiment_label', 'sentiment_score']].head())

if __name__ == "__main__":
    main()



