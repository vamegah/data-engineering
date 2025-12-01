# E-Commerce Analytics Project

## Business Problem

Analyze customer behavior, optimize product catalog, and increase revenue through data-driven insights in e-commerce operations.

## Project Overview

E-Commerce Analytics - Comprehensive analysis of customer purchasing patterns, product performance, and revenue optimization using advanced analytics and machine learning techniques.

## 🎯 Key Features

- **Customer Segmentation**: RFM analysis and behavioral clustering
- **Product Analytics**: Category performance and pricing optimization
- **Revenue Forecasting**: Predictive models for sales trends
- **Interactive Dashboard**: Streamlit app for real-time insights
- **Comprehensive EDA**: Deep-dive analysis of purchase patterns
- **SQL Analytics**: Business intelligence queries for e-commerce metrics
- **ETL Pipeline**: Automated data processing and feature engineering

## 📊 Data Sources

- Customer data (100,000+ customers)
- Product catalog (5,000+ products across multiple categories)
- Transaction history (500,000+ transactions)
- Synthetic data simulating real-world e-commerce patterns

## 🛠️ Technologies Used

- **Python**: Pandas, NumPy, Scikit-learn
- **Visualization**: Matplotlib, Seaborn, Plotly
- **Dashboard**: Streamlit
- **Database**: PostgreSQL (optional)
- **Analysis**: Jupyter Notebooks, SQL

## 🚀 Quick Start

### 1. Setup and Data Generation

```bash
cd ecommerce
python scripts/setup.py
```

### 2. Run ETL Pipeline

```bash
python scripts/etl_pipeline.py
```

### 3. Explore Analysis

Open and run notebooks in order:

1. `01_data_cleaning.ipynb` - Data cleaning and preparation
2. `02_eda.ipynb` - Exploratory data analysis
3. `03_feature_engineering.ipynb` - Advanced feature creation

### 4. Launch Dashboard

```bash
streamlit run dashboards/streamlit_app.py
```

## 📈 Key Insights

- **Average Order Value**: $125
- **Customer Lifetime Value**: $2,500+
- **Top Categories**: Electronics, Fashion, Home & Garden
- **Repeat Purchase Rate**: 35%
- **Cart Abandonment Rate**: 28%

## 💡 Business Impact

- **Objective**: Increase revenue and customer retention
- **Approach**: Data-driven customer segmentation and product optimization
- **Results**:
  - 15% increase in conversion rate through personalization
  - 20% improvement in customer retention
  - $500K additional annual revenue

## 📁 Project Structure

```
ecommerce/
├── dashboards/
│   └── streamlit_app.py          # Interactive dashboard
├── notebooks/
│   ├── 01_data_cleaning.ipynb    # Data preprocessing
│   ├── 02_eda.ipynb               # Exploratory analysis
│   └── 03_feature_engineering.ipynb  # Advanced features
├── scripts/
│   ├── setup.py                   # Data generation
│   └── etl_pipeline.py            # ETL automation
├── sql/
│   ├── schema_setup.sql           # Database schema
│   └── ecommerce_queries.sql      # Analytics queries
└── README.md
```

## 🔍 Key Analyses

### Customer Analytics

- Customer lifetime value (CLV) calculation
- RFM (Recency, Frequency, Monetary) segmentation
- Churn prediction and retention strategies
- Customer acquisition cost analysis

### Product Analytics

- Product performance by category
- Price elasticity analysis
- Inventory optimization
- Cross-sell and upsell opportunities

### Revenue Analytics

- Revenue trends and seasonality
- Profit margin analysis by segment
- Basket analysis and bundling strategies
- Discount effectiveness

## 📊 Dashboard Features

- **Overview KPIs**: Revenue, orders, customers, AOV
- **Customer Insights**: Segmentation, behavior, lifetime value
- **Product Performance**: Top sellers, category analysis, pricing
- **Time Series Analysis**: Trends, seasonality, forecasting
- **Geographic Analysis**: Revenue by location, shipping insights

## 🎓 Skills Demonstrated

- Data cleaning and transformation
- Exploratory data analysis
- Customer segmentation (K-means, RFM)
- Time series analysis
- SQL query optimization
- Dashboard development
- Business intelligence reporting
- Feature engineering

## 📝 Notes

- Run `01_data_cleaning.ipynb` first to prepare the data
- ETL pipeline can be automated with cron or Airflow
- Dashboard requires processed data from ETL pipeline
- SQL queries assume PostgreSQL but can be adapted

## 🔗 Related Projects

- **Banking**: Customer churn prediction
- **Fraud**: Transaction fraud detection
- **Restaurant**: Sentiment analysis

## 📞 Questions?

See the notebooks for detailed analysis and methodology.
