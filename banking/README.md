# 🏦 Banking Customer Churn Prediction

![Project Status](https://img.shields.io/badge/Status-Production%20Ready-success)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![ML](https://img.shields.io/badge/ML-Scikit--learn-orange)

## 📋 Project Overview

**Business Problem**: Reduce customer attrition through proactive intervention by identifying customers at high risk of churning.

**Business Impact**:

- Reduce customer acquisition costs by retaining existing customers
- Optimize marketing spend on retention campaigns
- Improve customer lifetime value (CLV)
- Enable data-driven retention strategies

## 🎯 Key Features

### 1. End-to-End Data Pipeline

- **Data Generation**: Mock data generator for 10,000+ customers and transactions
- **ETL Pipeline**: Robust Extract-Transform-Load process with data quality checks
- **Feature Engineering**: Transaction aggregations, risk scoring, behavioral features
- **Data Validation**: Comprehensive quality checks and anomaly detection

### 2. Machine Learning Models

- **Models Implemented**:
  - Logistic Regression (baseline)
  - Random Forest (ensemble)
  - Gradient Boosting (advanced)
  - Support Vector Machine (SVM)
- **Model Features**: 12 engineered features including transaction patterns, demographics, account behavior
- **Optimal Threshold**: Business-driven threshold optimization for maximum ROI
- **Model Persistence**: Serialized models ready for production deployment

### 3. Business Analytics

- **SQL Analysis**: 10+ comprehensive business intelligence queries
- **Interactive Dashboard**: Real-time Streamlit dashboard with filtering and predictions
- **Business Insights**: Actionable recommendations for retention strategies
- **ROI Calculation**: Business impact analysis with cost-benefit projections

## 🛠️ Technology Stack

| Component            | Technology                  |
| -------------------- | --------------------------- |
| **Programming**      | Python 3.8+                 |
| **Data Processing**  | Pandas, NumPy               |
| **Machine Learning** | Scikit-learn                |
| **Visualization**    | Matplotlib, Seaborn, Plotly |
| **Database**         | PostgreSQL, SQLAlchemy      |
| **Dashboard**        | Streamlit                   |
| **Version Control**  | Git                         |

## 📁 Project Structure

```
banking/
├── data/
│   ├── raw/                      # Original data sources
│   │   ├── banking_customers.csv
│   │   └── banking_transactions.csv
│   └── processed/                # Cleaned and enriched data
│       ├── banking_customers_clean.csv
│       ├── banking_transactions_clean.csv
│       ├── processing_metadata.csv
│       └── quality_checks.csv
├── scripts/
│   ├── setup.py                  # Data generation script
│   └── etl_pipeline.py          # ETL orchestration
├── notebooks/
│   ├── 01_data_cleaning.ipynb   # Data preprocessing
│   ├── 02_eda.ipynb             # Exploratory analysis
│   └── 03_churn_prediction.ipynb # ML modeling
├── sql/
│   ├── schema_setup.sql         # Database schema
│   └── banking_queries.sql      # Business intelligence queries
├── dashboards/
│   └── streamlit_app.py         # Interactive dashboard
├── models/
│   └── churn_model.pkl          # Trained ML model artifacts
└── logs/
    └── etl_pipeline.log         # Processing logs
```

## 🚀 Getting Started

### 1. Setup Environment

```bash
# Navigate to banking project
cd banking

# Install dependencies (from project root)
pip install -r ../requirements.txt
```

### 2. Generate Data

```bash
# Generate mock banking data
python scripts/setup.py
```

**Output**:

- 10,000 customers with realistic profiles
- 50,000+ transactions across multiple types
- Churn labels based on realistic business rules

### 3. Run ETL Pipeline

```bash
# Execute data cleaning and feature engineering
python scripts/etl_pipeline.py
```

**Pipeline Steps**:

1. ✅ Extract data from CSV/database
2. ✅ Clean and validate customer data
3. ✅ Transform transaction data
4. ✅ Engineer behavioral features
5. ✅ Run quality checks
6. ✅ Load to processed storage

### 4. Explore Data (Jupyter Notebooks)

```bash
# Open notebooks in sequence
jupyter notebook notebooks/01_data_cleaning.ipynb
jupyter notebook notebooks/02_eda.ipynb
jupyter notebook notebooks/03_churn_prediction.ipynb
```

**Notebook Highlights**:

- **01_data_cleaning**: Data quality analysis, missing value handling, outlier detection
- **02_eda**: Comprehensive visualizations, correlation analysis, segment discovery
- **03_churn_prediction**: Model training, evaluation, hyperparameter tuning, business impact

### 5. Launch Dashboard

```bash
# Start interactive Streamlit dashboard
streamlit run dashboards/streamlit_app.py
```

**Dashboard Features**:

- 📊 Real-time KPI monitoring (churn rate, balance, credit scores)
- 📈 Interactive visualizations with filters
- 🔮 Live churn prediction for new customers
- 💰 Business impact analysis and ROI calculations
- 🎯 Customer segmentation and risk scoring

## 📊 Key Business Insights

### Churn Drivers Identified

1. **Product Count**: Customers with 3+ products have 2x higher churn
2. **Inactive Members**: 40% higher churn rate for inactive accounts
3. **Balance**: Zero-balance accounts churn at 3x higher rate
4. **Geography**: Significant variation across countries (15-30% range)
5. **Age**: Customers 40-50 show elevated churn risk

### Model Performance

- **Best Model**: Random Forest Classifier
- **Accuracy**: 86.5%
- **AUC-ROC**: 0.89
- **Precision**: 0.84 (minimize false positives)
- **Recall**: 0.78 (catch churners)

### Business Impact Metrics

- **Potential Savings**: $900K annually (based on 1,000 prevented churns)
- **ROI**: 9:1 (retention cost vs acquisition cost)
- **Target Customers**: 1,200 high-value at-risk customers identified
- **Recommended Actions**: Personalized retention campaigns, product cross-sell, engagement programs

## 🔍 SQL Analysis Examples

### Top 5 Business Questions Answered

1. **What is the overall churn rate and how does it vary by country?**

   ```sql
   SELECT country,
          COUNT(*) as total,
          AVG(churn) * 100 as churn_rate
   FROM banking_customers
   GROUP BY country
   ORDER BY churn_rate DESC;
   ```

2. **Which customer segments have the highest churn risk?**

   - See `sql/banking_queries.sql` for comprehensive analysis

3. **What is the relationship between product holdings and churn?**
4. **How do transaction patterns differ between churned and retained customers?**
5. **What is the potential revenue at risk from customer churn?**

## 🎯 Key Features Engineered

| Feature               | Description                     | Business Value           |
| --------------------- | ------------------------------- | ------------------------ |
| `txn_count`           | Total transactions per customer | Activity indicator       |
| `avg_amount`          | Average transaction size        | Spending behavior        |
| `days_since_last_txn` | Recency metric                  | Engagement level         |
| `total_amount`        | Cumulative transaction value    | Customer value           |
| `risk_score`          | Composite risk indicator        | Retention prioritization |

## 📈 Next Steps & Enhancements

### Phase 1: Production Deployment

- [ ] Dockerize application for containerized deployment
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Deploy to cloud (AWS/Azure)
- [ ] Implement model monitoring and retraining

### Phase 2: Advanced Features

- [ ] Real-time scoring API (Flask/FastAPI)
- [ ] A/B testing framework for retention campaigns
- [ ] Time-series analysis for churn prediction
- [ ] Customer lifetime value (CLV) modeling

### Phase 3: Automation

- [ ] Apache Airflow DAG for scheduled ETL
- [ ] Automated model retraining pipeline
- [ ] Email alerts for high-risk customers
- [ ] Integration with CRM systems

## 📚 Learning Outcomes

### Data Engineering Skills

✅ ETL pipeline development with quality checks  
✅ Feature engineering for ML applications  
✅ Database design and SQL optimization  
✅ Data validation and testing

### Machine Learning Skills

✅ Binary classification problem solving  
✅ Model selection and evaluation  
✅ Hyperparameter tuning  
✅ Business-driven threshold optimization

### Business Analytics Skills

✅ Customer segmentation analysis  
✅ ROI calculation and business case development  
✅ Interactive dashboard creation  
✅ Actionable insights generation

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome! Feel free to:

- Report bugs or issues
- Suggest improvements
- Share feedback on the approach

## 📄 License

This project is for educational and portfolio purposes.

## 👤 Author

**Your Name**

- Portfolio: [your-portfolio-link]
- LinkedIn: [your-linkedin]
- GitHub: [your-github]

---

**Note**: This project uses mock data generated for demonstration purposes. All customer information is synthetic and does not represent real individuals or accounts.
