#!/usr/bin/env python3
"""
Data Engineering Portfolio - Main Setup Script

This script initializes all 7 projects in the portfolio:
1. E-commerce Sales Analysis
2. Healthcare Patient Analytics
3. Bank Customer Churn Prediction
4. HR Attrition Dashboard
5. Fraud Detection
6. Financial Stock Analysis
7. Restaurant Ratings & Review Analysis

Run this script to generate sample data and set up all projects.
"""

import sys
from pathlib import Path


class PortfolioSetup:
    def __init__(self):
        self.projects = {
            "ecommerce": {
                "name": "E-commerce Sales Analysis",
                "description": "Customer behavior and sales optimization",
                "dependencies": ["pandas", "sqlalchemy"],
                "status": "pending",
            },
            "healthcare": {
                "name": "Healthcare Patient Analytics",
                "description": "Patient outcomes and resource allocation",
                "dependencies": ["pandas", "scikit-learn"],
                "status": "pending",
            },
            "banking": {
                "name": "Bank Customer Churn Prediction",
                "description": "Customer retention and risk analysis",
                "dependencies": ["pandas", "scikit-learn"],
                "status": "pending",
            },
            "hr": {
                "name": "HR Attrition Dashboard",
                "description": "Employee turnover and workforce analytics",
                "dependencies": ["pandas", "plotly"],
                "status": "pending",
            },
            "fraud": {
                "name": "Fraud Detection",
                "description": "Anomaly detection and pattern recognition",
                "dependencies": ["pandas", "scikit-learn"],
                "status": "pending",
            },
            "financial": {
                "name": "Financial Stock Analysis",
                "description": "Market trends and portfolio optimization",
                "dependencies": ["pandas", "yfinance"],
                "status": "pending",
            },
            "restaurant": {
                "name": "Restaurant Ratings & Review Analysis",
                "description": "Customer sentiment and business insights",
                "dependencies": ["pandas", "nltk"],
                "status": "pending",
            },
        }

        self.setup_log = []
        self.success_count = 0

    def print_banner(self):
        """Display welcome banner"""
        banner = """
        🚀 Data Engineering Portfolio Setup
        ===================================
        
        This will set up 7 real-world data engineering projects:
        
        1. 📊 E-commerce Sales Analysis
        2. 🏥 Healthcare Patient Analytics  
        3. 🏦 Bank Customer Churn Prediction
        4. 👥 HR Attrition Dashboard
        5. 🕵️ Fraud Detection
        6. 📈 Financial Stock Analysis
        7. 🍽️ Restaurant Ratings & Review Analysis
        
        Estimated time: 2-3 minutes
        ===================================
        """
        print(banner)

    def check_dependencies(self):
        """Check if required packages are installed"""
        print("🔍 Checking dependencies...")

        required_packages = [
            "pandas",
            "numpy",
            "matplotlib",
            "seaborn",
            "jupyter",
            "sqlalchemy",
            "scikit-learn",
            "plotly",
            "streamlit",
        ]

        missing_packages = []

        for package in required_packages:
            try:
                __import__(package)
                print(f"   ✅ {package}")
            except ImportError:
                missing_packages.append(package)
                print(f"   ❌ {package}")

        if missing_packages:
            print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
            print("   Run: pip install -r requirements.txt")
            return False

        print("✅ All core dependencies are installed!")
        return True

    def create_directory_structure(self):
        """Create the project directory structure"""
        print("\n📁 Creating directory structure...")

        directories = [
            "shared/config",
            "shared/utils",
            "shared/scripts",
            "shared/data",
            "docs",
        ]

        # Create project directories
        for project in self.projects.keys():
            directories.extend(
                [
                    f"{project}/data/raw",
                    f"{project}/data/processed",
                    f"{project}/notebooks",
                    f"{project}/sql",
                    f"{project}/scripts",
                    f"{project}/dashboards",
                    f"{project}/docs",
                ]
            )

        created_count = 0
        for directory in directories:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                self.setup_log.append(f"Created directory: {directory}")
                created_count += 1
            except Exception as e:
                self.setup_log.append(f"Failed to create {directory}: {str(e)}")

        print(f"✅ Created {created_count} directories")
        return True

    def create_shared_utilities(self):
        """Create shared utility files"""
        print("\n🛠️  Creating shared utilities...")

        # Create database configuration
        db_config_content = '''import os
from sqlalchemy import create_engine
import psycopg2

class DatabaseConfig:
    """Database configuration for all projects"""
    
    DB_CONFIG = {
        'host': 'localhost',
        'database': 'portfolio_projects',
        'user': 'postgres',
        'password': 'your_password_here',
        'port': '5432'
    }
    
    @classmethod
    def get_connection_string(cls):
        return f"postgresql://{cls.DB_CONFIG['user']}:{cls.DB_CONFIG['password']}@{cls.DB_CONFIG['host']}:{cls.DB_CONFIG['port']}/{cls.DB_CONFIG['database']}"
    
    @classmethod
    def get_engine(cls):
        return create_engine(cls.get_connection_string())
    
    @classmethod
    def get_connection(cls):
        return psycopg2.connect(**cls.DB_CONFIG)
'''

        try:
            with open("shared/config/database.py", "w") as f:
                f.write(db_config_content)
            self.setup_log.append("Created: shared/config/database.py")
        except Exception as e:
            self.setup_log.append(f"Failed to create database config: {str(e)}")

        # Create helpers file
        helpers_content = '''import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def validate_data(df, df_name):
    """Basic data validation"""
    print(f"\\n📊 {df_name} Validation:")
    print(f"Shape: {df.shape}")
    print(f"Columns: {list(df.columns)}")
    print(f"Missing values:\\n{df.isnull().sum()}")
    print(f"Data types:\\n{df.dtypes}")
    
def calculate_business_metrics(df, date_column=None):
    """Calculate common business metrics"""
    metrics = {}
    metrics['total_records'] = len(df)
    
    if date_column and date_column in df.columns:
        metrics['date_range'] = {
            'start': df[date_column].min(),
            'end': df[date_column].max()
        }
    
    return metrics

def setup_plotting():
    """Setup consistent plotting style"""
    plt.style.use('seaborn-v0_8')
    sns.set_palette("husl")
    plt.rcParams['figure.figsize'] = (10, 6)
'''

        try:
            with open("shared/utils/helpers.py", "w") as f:
                f.write(helpers_content)
            self.setup_log.append("Created: shared/utils/helpers.py")
        except Exception as e:
            self.setup_log.append(f"Failed to create helpers: {str(e)}")

        print("✅ Shared utilities created")
        return True

    def create_data_generator(self):
        """Create the main data generator utility"""
        print("\n📊 Creating data generator...")

        # We'll create a simplified version first - we can expand later
        data_gen_content = '''import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class MockDataGenerator:
    """Generate realistic mock data for all portfolio projects"""
    
    def __init__(self, seed=42):
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
    
    def generate_ecommerce_data(self, n_customers=1000, n_products=100, n_transactions=5000):
        """Generate mock e-commerce data"""
        print("Generating e-commerce data...")
        
        # Customers
        cities = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix']
        customers = pd.DataFrame({
            'customer_id': [f'C{1000+i}' for i in range(n_customers)],
            'signup_date': [datetime(2023,1,1) + timedelta(days=random.randint(0, 365)) for _ in range(n_customers)],
            'location': [random.choice(cities) for _ in range(n_customers)],
            'tier': [random.choice(['Basic', 'Silver', 'Gold']) for _ in range(n_customers)]
        })
        
        # Products
        categories = ['Electronics', 'Clothing', 'Home', 'Books', 'Sports']
        products = pd.DataFrame({
            'product_id': [f'P{1000+i}' for i in range(n_products)],
            'product_name': [f'Product {i+1}' for i in range(n_products)],
            'category': [random.choice(categories) for _ in range(n_products)],
            'price': np.round(np.random.uniform(10, 500, n_products), 2)
        })
        
        # Transactions
        start_date = datetime(2023, 1, 1)
        transactions = pd.DataFrame({
            'transaction_id': [f'T{10000+i}' for i in range(n_transactions)],
            'customer_id': [random.choice(customers['customer_id']) for _ in range(n_transactions)],
            'product_id': [random.choice(products['product_id']) for _ in range(n_transactions)],
            'date': [start_date + timedelta(days=random.randint(0, 365)) for _ in range(n_transactions)],
            'quantity': [random.randint(1, 5) for _ in range(n_transactions)],
            'amount': np.round(np.random.uniform(20, 300, n_transactions), 2)
        })
        
        return customers, products, transactions
    
    def generate_healthcare_data(self, n_patients=500):
        """Generate simplified healthcare data"""
        print("Generating healthcare data...")
        
        facilities = pd.DataFrame({
            'facility_id': [f'FAC{1000+i}' for i in range(10)],
            'facility_name': [f'Hospital {i+1}' for i in range(10)],
            'location': [f'City {i+1}' for i in range(10)]
        })
        
        conditions = ['Hypertension', 'Diabetes', 'Asthma', 'Arthritis', 'Migraine']
        patients = pd.DataFrame({
            'patient_id': [f'PAT{10000+i}' for i in range(n_patients)],
            'age': np.random.randint(18, 90, n_patients),
            'gender': [random.choice(['Male', 'Female']) for _ in range(n_patients)],
            'condition': [random.choice(conditions) for _ in range(n_patients)],
            'admission_date': [datetime(2023,1,1) + timedelta(days=random.randint(0, 365)) for _ in range(n_patients)],
            'facility_id': [random.choice(facilities['facility_id']) for _ in range(n_patients)]
        })
        
        return patients, facilities
    
    # Simplified versions of other generators will be added as we build each project
        
    def save_all_datasets(self):
        """Generate and save all datasets"""
        print("Generating all datasets...")
        
        # E-commerce
        customers, products, transactions = self.generate_ecommerce_data()
        customers.to_csv('ecommerce/data/raw/customers.csv', index=False)
        products.to_csv('ecommerce/data/raw/products.csv', index=False)
        transactions.to_csv('ecommerce/data/raw/transactions.csv', index=False)
        
        # Healthcare
        patients, facilities = self.generate_healthcare_data()
        patients.to_csv('healthcare/data/raw/patients.csv', index=False)
        facilities.to_csv('healthcare/data/raw/facilities.csv', index=False)
        
        print("✅ Sample datasets generated!")
'''

        try:
            with open("shared/utils/data_generator.py", "w") as f:
                f.write(data_gen_content)
            self.setup_log.append("Created: shared/utils/data_generator.py")
            print("✅ Data generator created")
            return True
        except Exception as e:
            self.setup_log.append(f"Failed to create data generator: {str(e)}")
            return False

    def setup_individual_project(self, project_name):
        """Set up an individual project"""
        project_info = self.projects[project_name]

        print(f"\n🎯 Setting up {project_info['name']}...")
        print(f"   {project_info['description']}")

        try:
            # Add the shared directory to Python path
            sys.path.append("shared/utils")

            # Import and use the data generator
            from data_generator import MockDataGenerator
            sys.path.append(str(Path("shared/utils").resolve()))

            # Import and use the data generator
            from shared.utils.data_generator import MockDataGenerator

            generator = MockDataGenerator()
            if project_name == "ecommerce":
                customers, products, transactions = generator.generate_ecommerce_data()
                customers.to_csv(f"{project_name}/data/raw/customers.csv", index=False)
                products.to_csv(f"{project_name}/data/raw/products.csv", index=False)
                transactions.to_csv(
                    f"{project_name}/data/raw/transactions.csv", index=False
                )
                record_count = f"{len(customers)} customers, {len(products)} products, {len(transactions)} transactions"
            elif project_name == "healthcare":
                patients, facilities = generator.generate_healthcare_data()
                patients.to_csv(f"{project_name}/data/raw/patients.csv", index=False)
                facilities.to_csv(
                    f"{project_name}/data/raw/facilities.csv", index=False
                )
                record_count = f"{len(patients)} patients, {len(facilities)} facilities"
            else:
                # For other projects, create placeholder data for now
                import pandas as pd
                import numpy as np
                placeholder_df = pd.DataFrame(
                    {
                        "id": range(100),
                        "value": np.random.rand(100),
                        "category": ["A", "B", "C"] * 33 + ["A"],
                    }
                )
                placeholder_df.to_csv(
                    f"{project_name}/data/raw/sample_data.csv", index=False
                )
                record_count = "100 sample records"

            # Create project README
            self.create_project_readme(project_name)

            # Create basic notebook templates
            self.create_notebook_templates(project_name)

            self.projects[project_name]["status"] = "success"
            return True

        except Exception as e:
            error_msg = f"Failed to set up {project_name}: {str(e)}"
            self.setup_log.append(error_msg)
            print(f"❌ {error_msg}")
            self.projects[project_name]["status"] = "failed"
            return False
    def create_project_readme(self, project_name):
        """Create project-specific README files"""
        project_info = self.projects[project_name]
        
        readme_content = f"""# {project_info['name']}

## Project Overview
{project_info['description']}

## Business Problem
This project addresses key business challenges in the {project_name} domain through data analysis and engineering.

## Quick Start

1. **Explore the data**:
   ```
   jupyter lab notebooks/
   ```
2. **Run analysis**:
   ```
   jupyter nbconvert --to notebook --execute notebooks/03_attrition_analysis.ipynb
   ```
3. **View dashboards**:
   ```
   jupyter lab dashboards/
   streamlit run dashboards/app.py
   ```
## Project Structure

{project_name}/
├── data/
│   ├── raw/          # Raw data files
│   └── processed/    # Cleaned and transformed data
├── notebooks/        # Jupyter notebooks for analysis
├── sql/             # Database schemas and queries  
├── scripts/         # Python scripts for ETL
├── dashboards/      # Interactive Streamlit dashboards
└── docs/            # Project documentation

*Part of the Data Engineering Portfolio*
"""
        
        try:
            with open(f"{project_name}/README.md", "w") as f:
                f.write(readme_content)
            self.setup_log.append(f"Created README for {project_name}")
        except Exception as e:
            self.setup_log.append(f"Failed to create README for {project_name}: {str(e)}")
        # Create basic notebook templates for each project
        templates = {
            '01_data_cleaning.md': f'# {project_name.title()} - Data Cleaning',
            '02_eda.md': f'# {project_name.title()} - Exploratory Data Analysis', 
            '03_feature_engineering.md': f'# {project_name.title()} - Feature Engineering'
        }
        
        for notebook, title in templates.items():
            try:
                content = f"# {title}\n\n## Project: {self.projects[project_name]['name']}\n\nStart your analysis here!"
                with open(f"{project_name}/notebooks/{notebook}", "w") as f:
                    f.write(content)
            except Exception as e:
                self.setup_log.append(f"Failed to create notebook {notebook} for {project_name}: {str(e)}")

    def show_progress(self):
        """Show current setup progress"""
        print(f"\n📊 Progress: {self.success_count}/{len(self.projects)} projects completed")
        
        for project, info in self.projects.items():
            status_icon = "✅" if info['status'] == 'success' else "❌" if info['status'] == 'failed' else "⏳"
            print(f"   {status_icon} {info['name']}")

    def generate_setup_report(self, total_time):
        """Generate a setup completion report"""
        print("\n" + "="*60)
        print("📊 SETUP COMPLETION REPORT")
        print("="*60)
        
        print(f"\n✅ Successful: {self.success_count}/{len(self.projects)} projects")
        print(f"⏱️  Total time: {total_time:.2f} seconds")
        
        print("\n📋 Recent Log:")
        for log_entry in self.setup_log[-10:]:
            print(f"   {log_entry}")
        
        print(f"\n🎯 Next Steps:")
        print("1. Start with any project: 'jupyter lab [project_name]/notebooks/'")
        print("2. Run individual project setups if needed")
        print("3. Check project README files for specific instructions")
        
        if self.success_count == len(self.projects):
            print("\n🎉 All projects are ready! Happy data engineering! 🚀")
        else:
            print(f"\n⚠️  {len(self.projects) - self.success_count} projects need attention.")

def main():
    parser = argparse.ArgumentParser(description='Setup Data Engineering Portfolio')
    parser.add_argument('--projects', nargs='+', 
                       choices=['ecommerce', 'healthcare', 'banking', 'hr', 'fraud', 'financial', 'restaurant', 'all'],
                       default='all',
                       help='Specific projects to set up (default: all)')
    parser.add_argument('--skip-deps', action='store_true',
                       help='Skip dependency check')
    parser.add_argument('--skip-dirs', action='store_true',
                       help='Skip directory creation')
    
    args = parser.parse_args()
    
    setup = PortfolioSetup()
    setup.print_banner()
    
    # Check dependencies
    if not args.skip_deps and not setup.check_dependencies():
        print("❌ Please install required dependencies from requirements.txt")
        return
    
    # Create directory structure
    if not args.skip_dirs:
        if not setup.create_directory_structure():
            print("❌ Failed to create directory structure")
            return
    
    # Create shared utilities
    if not setup.create_shared_utilities():
        print("❌ Failed to create shared utilities")
        return
    
    # Create data generator
    if not setup.create_data_generator():
        print("❌ Failed to create data generator")
        return
    
    # Determine which projects to set up
    if 'all' in args.projects:
        projects_to_setup = list(setup.projects.keys())
    else:
        projects_to_setup = args.projects
    
    # Setup projects
    start_time = time.time()
    
    for project in projects_to_setup:
        if project in setup.projects:
            if setup.setup_individual_project(project):
                setup.success_count += 1
            setup.show_progress()
        else:
            print(f"❌ Unknown project: {project}")
    
    end_time = time.time()
    total_time = end_time - start_time
    
    # Generate final report
    setup.generate_setup_report(total_time)

if __name__ == "__main__":
    main()