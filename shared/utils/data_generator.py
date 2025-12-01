"""
Mock Data Generator Module
Generate realistic, business-relevant mock data for all 7 portfolio projects
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import logging
from typing import Dict, List, Tuple, Any
import json
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockDataGenerator:
    """
    Generate realistic mock data for data engineering portfolio projects
    Includes 7 business domains with proper relationships and realistic patterns
    """

    def __init__(self, seed: int = 42):
        """
        Initialize the data generator with a seed for reproducibility

        Args:
            seed: Random seed for reproducible data generation
        """
        self.seed = seed
        np.random.seed(seed)
        random.seed(seed)
        logger.info(f"MockDataGenerator initialized with seed: {seed}")

        # Business domain configurations
        self._setup_business_configs()

    def _setup_business_configs(self):
        """Setup business-specific configurations and constants"""

        # E-commerce configurations
        self.ecommerce_config = {
            "cities": [
                "New York",
                "Los Angeles",
                "Chicago",
                "Houston",
                "Phoenix",
                "Philadelphia",
                "San Antonio",
                "San Diego",
                "Dallas",
                "San Jose",
            ],
            "customer_tiers": ["Basic", "Silver", "Gold", "Platinum"],
            "product_categories": [
                "Electronics",
                "Clothing",
                "Home & Kitchen",
                "Books",
                "Sports & Outdoors",
                "Beauty",
                "Toys",
                "Grocery",
            ],
            "regions": ["North", "South", "East", "West"],
        }

        # Healthcare configurations
        self.healthcare_config = {
            "facility_types": [
                "General Hospital",
                "Specialty Clinic",
                "Urgent Care",
                "Research Center",
            ],
            "specialties": [
                "Cardiology",
                "Oncology",
                "Neurology",
                "Orthopedics",
                "Pediatrics",
                "Emergency",
            ],
            "conditions": [
                "Hypertension",
                "Diabetes",
                "Arthritis",
                "Asthma",
                "Cancer",
                "Heart Disease",
                "COPD",
                "Depression",
                "Obesity",
                "Stroke",
            ],
            "treatment_types": [
                "Medication",
                "Surgery",
                "Therapy",
                "Radiation",
                "Rehabilitation",
                "Counseling",
            ],
            "outcomes": ["Successful", "Improved", "No Change", "Worsened"],
            "insurance_types": ["Private", "Medicare", "Medicaid", "Self-Pay"],
        }

        # Banking configurations
        self.banking_config = {
            "countries": [
                "United States",
                "United Kingdom",
                "Germany",
                "France",
                "Spain",
            ],
            "transaction_types": [
                "Transfer",
                "Withdrawal",
                "Deposit",
                "Payment",
                "Purchase",
            ],
            "merchants": [
                "Amazon",
                "Walmart",
                "Netflix",
                "Spotify",
                "Starbucks",
                "Apple",
                "Google",
                "Electric Co",
                "Water Co",
                "Mortgage Co",
            ],
            "locations": ["Online", "In-Store", "ATM"],
        }

        # HR configurations
        self.hr_config = {
            "departments": [
                "Sales",
                "Technology",
                "Marketing",
                "Finance",
                "HR",
                "Operations",
                "R&D",
                "Customer Service",
            ],
            "education_levels": ["High School", "Bachelor", "Master", "PhD"],
            "education_fields": [
                "Life Sciences",
                "Medical",
                "Technical",
                "Marketing",
                "Other",
            ],
            "marital_statuses": ["Single", "Married", "Divorced"],
            "exit_reasons": [
                "Better opportunity",
                "Career change",
                "Relocation",
                "Work-life balance",
                "Management issues",
                "Salary",
                "Company culture",
                "Personal reasons",
            ],
        }

        # Job roles by department
        self.job_roles = {
            "Sales": [
                "Sales Representative",
                "Account Executive",
                "Sales Manager",
                "BD Manager",
            ],
            "Technology": [
                "Software Engineer",
                "Data Scientist",
                "DevOps",
                "IT Support",
                "CTO",
            ],
            "Marketing": [
                "Marketing Specialist",
                "Content Writer",
                "SEO Analyst",
                "CMO",
            ],
            "Finance": ["Financial Analyst", "Accountant", "Controller", "CFO"],
            "HR": ["HR Specialist", "Recruiter", "HR Manager", "CHRO"],
            "Operations": [
                "Operations Manager",
                "Logistics Coordinator",
                "Supply Chain Analyst",
            ],
            "R&D": ["Research Scientist", "Lab Technician", "Research Director"],
            "Customer Service": [
                "Customer Support",
                "Service Manager",
                "Support Specialist",
            ],
        }

        # Fraud detection configurations
        self.fraud_config = {
            "transaction_categories": [
                "Retail",
                "Travel",
                "Food",
                "Entertainment",
                "Utilities",
                "Healthcare",
                "Education",
                "Transportation",
            ],
            "device_types": ["Mobile", "Desktop", "Tablet"],
            "locations": ["Domestic", "International"],
        }

        # Merchant categories for fraud detection
        self.merchants_by_category = {
            "Retail": ["Amazon", "Walmart", "Target", "Best Buy", "Home Depot"],
            "Travel": [
                "Expedia",
                "Booking.com",
                "Airbnb",
                "United Airlines",
                "Marriott",
            ],
            "Food": ["McDonalds", "Starbucks", "Subway", "Dominoes", "Chipotle"],
            "Entertainment": [
                "Netflix",
                "Spotify",
                "Movie Theater",
                "Concert",
                "Sports Event",
            ],
            "Utilities": [
                "Electric Co",
                "Water Co",
                "Internet Provider",
                "Gas Company",
            ],
            "Healthcare": ["Hospital", "Pharmacy", "Dental Clinic", "Optometrist"],
            "Education": [
                "University",
                "Online Course",
                "Bookstore",
                "Training Center",
            ],
            "Transportation": ["Uber", "Lyft", "Taxi", "Gas Station", "Auto Repair"],
        }

        # Financial configurations
        self.financial_config = {
            "sectors": [
                "Technology",
                "Healthcare",
                "Financial",
                "Consumer",
                "Industrial",
                "Energy",
                "Utilities",
                "Real Estate",
            ],
            "market_caps": ["Large", "Mid", "Small"],
        }

        # Restaurant configurations
        self.restaurant_config = {
            "cuisines": [
                "Italian",
                "Chinese",
                "Mexican",
                "Indian",
                "American",
                "Japanese",
                "Thai",
                "French",
                "Mediterranean",
                "BBQ",
                "Vegetarian",
                "Seafood",
            ],
            "price_ranges": ["$", "$$", "$$$", "$$$$"],
        }

        # Dishes by cuisine for restaurant reviews
        self.dishes_by_cuisine = {
            "Italian": ["Pasta Carbonara", "Margherita Pizza", "Tiramisu", "Lasagna"],
            "Chinese": ["Kung Pao Chicken", "Dim Sum", "Fried Rice", "Hot Pot"],
            "Mexican": ["Tacos", "Guacamole", "Burrito", "Quesadilla"],
            "Indian": ["Butter Chicken", "Biryani", "Naan", "Samosa"],
            "American": ["Burger", "Steak", "BBQ Ribs", "Mac and Cheese"],
            "Japanese": ["Sushi", "Ramen", "Tempura", "Teriyaki"],
            "Thai": ["Pad Thai", "Green Curry", "Tom Yum", "Spring Rolls"],
            "French": ["Croissant", "Coq au Vin", "Crème Brûlée", "Ratatouille"],
            "Mediterranean": ["Hummus", "Falafel", "Shawarma", "Baklava"],
            "BBQ": ["Brisket", "Pulled Pork", "Ribs", "Cornbread"],
            "Vegetarian": ["Buddha Bowl", "Veggie Burger", "Salad", "Stir Fry"],
            "Seafood": ["Grilled Salmon", "Fish Tacos", "Lobster Roll", "Calamari"],
        }

        # Review templates for sentiment analysis
        self.review_templates = [
            "Great food and excellent service! Will definitely come back.",
            "Average experience. Food was okay but nothing special.",
            "Amazing flavors and generous portions. Highly recommended!",
            "Disappointing. Service was slow and food was cold.",
            "Best {cuisine} in town! The {dish} was incredible.",
            "Overpriced for what you get. Won't be returning.",
            "Cozy atmosphere and friendly staff. Perfect for date night.",
            "Food was good but the wait was too long.",
            "Absolutely loved everything! From appetizers to dessert.",
            "Not worth the hype. There are better options nearby.",
        ]

    def generate_ecommerce_data(
        self,
        n_customers: int = 1000,
        n_products: int = 100,
        n_transactions: int = 10000,
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate e-commerce data for sales analysis

        Args:
            n_customers: Number of customers to generate
            n_products: Number of products to generate
            n_transactions: Number of transactions to generate

        Returns:
            Tuple of (customers_df, products_df, transactions_df)
        """
        logger.info(
            f"Generating e-commerce data: {n_customers} customers, {n_products} products, {n_transactions} transactions"
        )

        # Generate customers data
        customers = pd.DataFrame(
            {
                "customer_id": [f"CUST{10000 + i}" for i in range(n_customers)],
                "signup_date": [
                    datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1000))
                    for _ in range(n_customers)
                ],
                "location": [
                    random.choice(self.ecommerce_config["cities"])
                    for _ in range(n_customers)
                ],
                "tier": [
                    random.choice(self.ecommerce_config["customer_tiers"])
                    for _ in range(n_customers)
                ],
                "loyalty_score": np.round(np.random.beta(2, 2, n_customers) * 100, 2),
            }
        )

        # Generate products data
        products = pd.DataFrame(
            {
                "product_id": [f"PROD{1000 + i}" for i in range(n_products)],
                "product_name": [f"Product {i+1}" for i in range(n_products)],
                "category": [
                    random.choice(self.ecommerce_config["product_categories"])
                    for _ in range(n_products)
                ],
                "price": np.round(np.random.lognormal(3, 0.8, n_products), 2),
                "cost": np.round(np.random.lognormal(2, 0.6, n_products), 2),
                "inventory": np.random.randint(10, 1000, n_products),
            }
        )

        # Calculate profit margin
        products["profit_margin"] = np.round(
            (products["price"] - products["cost"]) / products["price"] * 100, 2
        )

        # Generate transactions data
        start_date = datetime(2023, 1, 1)

        transactions = pd.DataFrame(
            {
                "transaction_id": [f"TXN{50000 + i}" for i in range(n_transactions)],
                "customer_id": [
                    random.choice(customers["customer_id"])
                    for _ in range(n_transactions)
                ],
                "product_id": [
                    random.choice(products["product_id"]) for _ in range(n_transactions)
                ],
                "date": [
                    start_date + timedelta(days=random.randint(0, 365))
                    for _ in range(n_transactions)
                ],
                "quantity": np.random.randint(1, 6, n_transactions),
                "region": [
                    random.choice(self.ecommerce_config["regions"])
                    for _ in range(n_transactions)
                ],
                "discount": np.round(
                    np.random.beta(1, 5, n_transactions) * 30, 2
                ),  # Most transactions have small discounts
            }
        )

        # Merge with products to get prices and calculate totals
        transactions = transactions.merge(
            products[["product_id", "price"]], on="product_id", how="left"
        )
        transactions["total_amount"] = np.round(
            transactions["quantity"]
            * transactions["price"]
            * (1 - transactions["discount"] / 100),
            2,
        )

        logger.info("✅ E-commerce data generation completed")
        return customers, products, transactions

    def generate_healthcare_data(
        self, n_patients: int = 2000, n_treatments: int = 5000, n_facilities: int = 50
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate healthcare data for patient analytics

        Args:
            n_patients: Number of patients to generate
            n_treatments: Number of treatments to generate
            n_facilities: Number of facilities to generate

        Returns:
            Tuple of (patients_df, treatments_df, facilities_df)
        """
        logger.info(
            f"Generating healthcare data: {n_patients} patients, {n_treatments} treatments, {n_facilities} facilities"
        )

        # Generate facilities data
        facilities = pd.DataFrame(
            {
                "facility_id": [f"FAC{1000 + i}" for i in range(n_facilities)],
                "facility_name": [
                    f'{random.choice(["City", "Regional", "Community", "Metro"])} {random.choice(self.healthcare_config["facility_types"])}'
                    for _ in range(n_facilities)
                ],
                "facility_type": [
                    random.choice(self.healthcare_config["facility_types"])
                    for _ in range(n_facilities)
                ],
                "specialty": [
                    random.choice(self.healthcare_config["specialties"])
                    for _ in range(n_facilities)
                ],
                "location": [f"City {i % 10 + 1}" for i in range(n_facilities)],
                "bed_capacity": np.random.randint(50, 500, n_facilities),
                "established_year": np.random.randint(1990, 2020, n_facilities),
                "quality_rating": np.round(np.random.uniform(3, 5, n_facilities), 1),
            }
        )

        # Generate patients data
        patients = pd.DataFrame(
            {
                "patient_id": [f"PAT{10000 + i}" for i in range(n_patients)],
                "age": np.random.randint(18, 90, n_patients),
                "gender": [
                    random.choice(["Male", "Female"]) for _ in range(n_patients)
                ],
                "blood_type": [
                    random.choice(["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-"])
                    for _ in range(n_patients)
                ],
                "primary_condition": [
                    random.choice(self.healthcare_config["conditions"])
                    for _ in range(n_patients)
                ],
                "admission_date": [
                    datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
                    for _ in range(n_patients)
                ],
                "facility_id": [
                    random.choice(facilities["facility_id"]) for _ in range(n_patients)
                ],
                "insurance_type": [
                    random.choice(self.healthcare_config["insurance_types"])
                    for _ in range(n_patients)
                ],
                "severity": np.random.randint(1, 5, n_patients),  # 1=Low, 5=Critical
            }
        )

        # Generate discharge dates (1-30 days after admission)
        patients["discharge_date"] = patients["admission_date"] + pd.to_timedelta(
            np.random.randint(1, 30, len(patients)), unit="d"
        )

        # Calculate length of stay
        patients["length_of_stay"] = (
            patients["discharge_date"] - patients["admission_date"]
        ).dt.days

        # Generate readmission flag (some patients readmitted within 30 days)
        readmission_prob = 0.1 + (
            patients["severity"] / 10
        )  # Higher severity = higher readmission chance
        patients["readmission_30_days"] = np.random.binomial(
            1, np.clip(readmission_prob, 0, 0.5)
        )

        # Generate treatments data
        treatments = pd.DataFrame(
            {
                "treatment_id": [f"TRT{50000 + i}" for i in range(n_treatments)],
                "patient_id": [
                    random.choice(patients["patient_id"]) for _ in range(n_treatments)
                ],
                "treatment_type": [
                    random.choice(self.healthcare_config["treatment_types"])
                    for _ in range(n_treatments)
                ],
                "treatment_date": [
                    datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
                    for _ in range(n_treatments)
                ],
                "cost": np.round(
                    np.random.lognormal(5, 1.2, n_treatments), 2
                ),  # Log-normal for realistic cost distribution
                "duration_days": np.random.randint(1, 90, n_treatments),
                "outcome": [
                    random.choice(self.healthcare_config["outcomes"])
                    for _ in range(n_treatments)
                ],
                "medication_prescribed": np.random.choice(
                    [True, False], n_treatments, p=[0.7, 0.3]
                ),
            }
        )

        # Add success probability based on treatment type and duration
        success_base = {
            "Medication": 0.7,
            "Therapy": 0.6,
            "Rehabilitation": 0.5,
            "Counseling": 0.5,
            "Surgery": 0.8,
            "Radiation": 0.6,
        }

        treatments["success_probability"] = treatments["treatment_type"].map(
            success_base
        )
        treatments["success_probability"] += (
            treatments["duration_days"] / 100
        )  # Longer treatment = better outcome

        logger.info("✅ Healthcare data generation completed")
        return patients, treatments, facilities

    def generate_banking_data(
        self, n_customers: int = 10000, n_transactions: int = 50000
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate banking data for churn prediction

        Args:
            n_customers: Number of banking customers to generate
            n_transactions: Number of transactions to generate

        Returns:
            Tuple of (customers_df, transactions_df)
        """
        logger.info(
            f"Generating banking data: {n_customers} customers, {n_transactions} transactions"
        )

        # Generate customers data with realistic distributions
        customers = pd.DataFrame(
            {
                "customer_id": [f"BANK{10000 + i}" for i in range(n_customers)],
                "credit_score": np.clip(
                    np.random.normal(650, 100, n_customers), 300, 850
                ).astype(int),
                "country": [
                    random.choice(self.banking_config["countries"])
                    for _ in range(n_customers)
                ],
                "gender": [
                    random.choice(["Male", "Female"]) for _ in range(n_customers)
                ],
                "age": np.random.randint(18, 80, n_customers),
                "tenure": np.random.exponential(3, n_customers).astype(
                    int
                ),  # Most customers are relatively new
                "balance": np.round(np.random.exponential(5000, n_customers), 2),
                "products_number": np.random.choice(
                    [1, 2, 3, 4, 5], n_customers, p=[0.3, 0.25, 0.2, 0.15, 0.1]
                ),
                "credit_card": np.random.choice([0, 1], n_customers, p=[0.3, 0.7]),
                "active_member": np.random.choice([0, 1], n_customers, p=[0.4, 0.6]),
                "estimated_salary": np.round(
                    np.random.lognormal(10.5, 0.4, n_customers), 2
                ),
            }
        )

        # Generate churn with realistic business logic
        churn_probability = (
            0.05  # Base churn rate
            + (customers["balance"] < 100) * 0.3  # Low balance = higher churn
            + (customers["credit_score"] < 580) * 0.25  # Poor credit = higher churn
            + (customers["active_member"] == 0) * 0.2  # Inactive = higher churn
            + (customers["products_number"] == 1)
            * 0.15  # Single product = higher churn
            + (customers["tenure"] < 1) * 0.1  # New customers = higher churn
        )

        customers["churn"] = np.random.binomial(1, np.clip(churn_probability, 0, 0.8))

        # Generate transactions data
        start_date = datetime(2023, 1, 1)

        transactions = pd.DataFrame(
            {
                "transaction_id": [f"TXN{100000 + i}" for i in range(n_transactions)],
                "customer_id": [
                    random.choice(customers["customer_id"])
                    for _ in range(n_transactions)
                ],
                "transaction_type": [
                    random.choice(self.banking_config["transaction_types"])
                    for _ in range(n_transactions)
                ],
                "amount": np.round(np.random.lognormal(3, 1.5, n_transactions), 2),
                "date": [
                    start_date + timedelta(days=random.randint(0, 365))
                    for _ in range(n_transactions)
                ],
                "merchant": [
                    random.choice(self.banking_config["merchants"])
                    for _ in range(n_transactions)
                ],
                "location": [
                    random.choice(self.banking_config["locations"])
                    for _ in range(n_transactions)
                ],
            }
        )

        # Adjust amounts based on transaction type
        transactions.loc[
            transactions["transaction_type"].isin(["Withdrawal", "Payment"]), "amount"
        ] *= -1

        # Generate fraud labels with realistic patterns
        fraud_probability = (
            0.005  # Base fraud rate (0.5%)
            + (
                transactions["amount"].abs()
                > transactions["amount"].abs().quantile(0.95)
            )
            * 0.1
            + (transactions["location"] == "Online") * 0.02
            + (transactions["transaction_type"].isin(["Purchase", "Withdrawal"])) * 0.01
        )

        transactions["is_fraudulent"] = np.random.binomial(
            1, np.clip(fraud_probability, 0, 0.15)
        )

        logger.info("✅ Banking data generation completed")
        return customers, transactions

    def generate_hr_data(
        self, n_employees: int = 1500
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate HR data for attrition analysis

        Args:
            n_employees: Number of employees to generate

        Returns:
            Tuple of (employees_df, exit_interviews_df)
        """
        logger.info(f"Generating HR data: {n_employees} employees")

        # Generate employees data
        employees = pd.DataFrame(
            {
                "employee_id": [f"EMP{1000 + i}" for i in range(n_employees)],
                "department": [
                    random.choice(self.hr_config["departments"])
                    for _ in range(n_employees)
                ],
                "education": [
                    random.choice(self.hr_config["education_levels"])
                    for _ in range(n_employees)
                ],
                "education_field": [
                    random.choice(self.hr_config["education_fields"])
                    for _ in range(n_employees)
                ],
                "gender": [
                    random.choice(["Male", "Female"]) for _ in range(n_employees)
                ],
                "age": np.random.randint(22, 65, n_employees),
                "tenure": np.random.exponential(5, n_employees).astype(
                    int
                ),  # Most employees have shorter tenure
                "marital_status": [
                    random.choice(self.hr_config["marital_statuses"])
                    for _ in range(n_employees)
                ],
                "distance_from_home": np.round(
                    np.random.exponential(15, n_employees), 1
                ),  # Miles
            }
        )

        # Assign job roles based on department
        employees["job_role"] = employees["department"].apply(
            lambda dept: random.choice(self.job_roles.get(dept, ["Specialist"]))
        )

        # Generate salary based on role, education, and tenure
        base_salary = {
            "Sales Representative": 50000,
            "Account Executive": 65000,
            "Sales Manager": 85000,
            "BD Manager": 95000,
            "Software Engineer": 80000,
            "Data Scientist": 95000,
            "DevOps": 85000,
            "IT Support": 55000,
            "CTO": 150000,
            "Marketing Specialist": 55000,
            "Content Writer": 45000,
            "SEO Analyst": 60000,
            "CMO": 120000,
            "Financial Analyst": 65000,
            "Accountant": 55000,
            "Controller": 85000,
            "CFO": 130000,
            "HR Specialist": 50000,
            "Recruiter": 45000,
            "HR Manager": 75000,
            "CHRO": 110000,
            "Operations Manager": 70000,
            "Logistics Coordinator": 45000,
            "Supply Chain Analyst": 60000,
            "Research Scientist": 75000,
            "Lab Technician": 45000,
            "Research Director": 95000,
            "Customer Support": 40000,
            "Service Manager": 60000,
            "Support Specialist": 45000,
        }

        employees["base_salary"] = employees["job_role"].map(base_salary)

        # Adjust salary based on education
        education_multiplier = {
            "High School": 0.8,
            "Bachelor": 1.0,
            "Master": 1.3,
            "PhD": 1.6,
        }
        employees["base_salary"] *= employees["education"].map(education_multiplier)

        # Adjust salary based on tenure (2% per year)
        employees["base_salary"] *= 1 + employees["tenure"] * 0.02

        # Add some random variation
        employees["base_salary"] *= np.random.uniform(0.9, 1.1, n_employees)
        employees["salary"] = np.round(employees["base_salary"], 2)
        employees.drop("base_salary", axis=1, inplace=True)

        # Generate other employee metrics
        employees["bonus"] = np.round(
            employees["salary"] * np.random.beta(2, 5, n_employees) * 0.3, 2
        )  # 0-30% bonus
        employees["job_satisfaction"] = np.random.randint(
            1, 6, n_employees
        )  # 1-5 scale
        employees["performance_rating"] = np.random.randint(
            1, 6, n_employees
        )  # 1-5 scale
        employees["overtime"] = np.random.choice(
            ["Yes", "No"], n_employees, p=[0.3, 0.7]
        )

        # Generate attrition with realistic business logic
        attrition_probability = (
            0.05  # Base attrition rate
            + (employees["job_satisfaction"] <= 2) * 0.3
            + (employees["performance_rating"] <= 2) * 0.2
            + (employees["overtime"] == "Yes") * 0.15
            + (employees["tenure"] < 1) * 0.1
            + (employees["salary"] < employees["salary"].quantile(0.25)) * 0.1
        )

        employees["attrition"] = [
            "Yes" if x else "No"
            for x in np.random.binomial(1, np.clip(attrition_probability, 0, 0.7))
        ]

        # Generate exit interviews for employees who left
        attrition_employees = employees[employees["attrition"] == "Yes"]

        exit_interviews = pd.DataFrame(
            {
                "employee_id": attrition_employees["employee_id"].tolist(),
                "exit_date": [
                    datetime(2023, 1, 1) + timedelta(days=random.randint(0, 365))
                    for _ in range(len(attrition_employees))
                ],
                "reason": [
                    random.choice(self.hr_config["exit_reasons"])
                    for _ in range(len(attrition_employees))
                ],
                "satisfaction_score": np.random.randint(1, 6, len(attrition_employees)),
                "would_recommend": np.random.choice(
                    ["Yes", "No"], len(attrition_employees), p=[0.4, 0.6]
                ),
            }
        )

        logger.info("✅ HR data generation completed")
        return employees, exit_interviews

    def generate_fraud_data(
        self, n_users: int = 5000, n_transactions: int = 100000
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate fraud detection data

        Args:
            n_users: Number of users to generate
            n_transactions: Number of transactions to generate

        Returns:
            Tuple of (users_df, transactions_df)
        """
        logger.info(
            f"Generating fraud detection data: {n_users} users, {n_transactions} transactions"
        )

        # Generate users data
        users = pd.DataFrame(
            {
                "user_id": [f"USER{10000 + i}" for i in range(n_users)],
                "signup_date": [
                    datetime(2022, 1, 1) + timedelta(days=random.randint(0, 730))
                    for _ in range(n_users)
                ],
                "location": [f"City {i % 20 + 1}" for i in range(n_users)],
                "device_type": [
                    random.choice(self.fraud_config["device_types"])
                    for _ in range(n_users)
                ],
                "account_age_days": np.random.randint(1, 730, n_users),
                "trust_score": np.round(
                    np.random.beta(5, 2, n_users) * 100, 2
                ),  # Most users have high trust score
            }
        )

        # Generate transactions data
        start_date = datetime(2023, 1, 1)

        transactions = pd.DataFrame(
            {
                "transaction_id": [f"TXN{500000 + i}" for i in range(n_transactions)],
                "user_id": [
                    random.choice(users["user_id"]) for _ in range(n_transactions)
                ],
                "amount": np.round(np.random.lognormal(4, 1.5, n_transactions), 2),
                "transaction_date": [
                    start_date
                    + timedelta(
                        days=random.randint(0, 365),
                        hours=random.randint(0, 23),
                        minutes=random.randint(0, 59),
                    )
                    for _ in range(n_transactions)
                ],
                "category": [
                    random.choice(self.fraud_config["transaction_categories"])
                    for _ in range(n_transactions)
                ],
                "location": [
                    random.choice(self.fraud_config["locations"])
                    for _ in range(n_transactions)
                ],
                "device_used": [
                    random.choice(self.fraud_config["device_types"])
                    for _ in range(n_transactions)
                ],
                "hour_of_day": [random.randint(0, 23) for _ in range(n_transactions)],
            }
        )

        # Assign merchants based on category
        transactions["merchant"] = transactions["category"].apply(
            lambda cat: random.choice(
                self.merchants_by_category.get(cat, ["Generic Store"])
            )
        )

        # Generate fraud labels with realistic patterns
        fraud_probability = (
            0.01  # Base fraud rate (1%)
            + (transactions["amount"] > transactions["amount"].quantile(0.95))
            * 0.15  # Large transactions
            + (transactions["location"] == "International")
            * 0.08  # International transactions
            + (transactions["hour_of_day"].between(1, 5))
            * 0.05  # Late night transactions
            + (transactions["category"].isin(["Travel", "Electronics"]))
            * 0.03  # High-risk categories
            + (
                transactions["device_used"]
                != transactions["user_id"].map(  # Device mismatch
                    users.set_index("user_id")["device_type"].to_dict()
                )
            )
            * 0.1
        )

        # Add user trust score factor
        user_trust_map = users.set_index("user_id")["trust_score"].to_dict()
        transactions["user_trust"] = transactions["user_id"].map(user_trust_map)
        fraud_probability += ((100 - transactions["user_trust"]) / 100) * 0.2

        transactions["is_fraud"] = np.random.binomial(
            1, np.clip(fraud_probability, 0, 0.4)
        )
        transactions.drop("user_trust", axis=1, inplace=True)

        logger.info("✅ Fraud detection data generation completed")
        return users, transactions

    def generate_financial_data(
        self, n_stocks: int = 50, n_days: int = 252
    ) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Generate financial stock market data

        Args:
            n_stocks: Number of stocks to generate
            n_days: Number of trading days to generate

        Returns:
            Tuple of (stocks_df, price_data_df)
        """
        logger.info(
            f"Generating financial data: {n_stocks} stocks, {n_days} days of price data"
        )

        stocks = []
        price_data = []

        # Base market parameters
        market_volatility = 0.015  # Daily market volatility
        start_date = datetime(2023, 1, 1)

        for i in range(n_stocks):
            stock_id = f"STK{100 + i}"
            sector = random.choice(self.financial_config["sectors"])
            market_cap = random.choice(self.financial_config["market_caps"])

            # Set base parameters based on market cap
            if market_cap == "Large":
                base_price = np.random.uniform(50, 300)
                daily_volatility = (
                    market_volatility * 0.8
                )  # Large caps are less volatile
            elif market_cap == "Mid":
                base_price = np.random.uniform(20, 100)
                daily_volatility = market_volatility * 1.2  # Mid caps are more volatile
            else:  # Small
                base_price = np.random.uniform(5, 50)
                daily_volatility = (
                    market_volatility * 1.5
                )  # Small caps are most volatile

            # Stock metadata
            stocks.append(
                {
                    "stock_id": stock_id,
                    "symbol": f"S{i:03d}",
                    "company_name": f'{random.choice(["Global", "National", "First", "Advanced"])} {sector} Inc.',
                    "sector": sector,
                    "market_cap": market_cap,
                    "dividend_yield": np.round(
                        np.random.beta(2, 5, 1)[0] * 0.05, 4
                    ),  # Most stocks have low dividend
                    "beta": np.round(
                        np.random.uniform(0.5, 1.8, 1)[0], 2
                    ),  # Market sensitivity
                }
            )

            # Generate price series using geometric brownian motion
            prices = [base_price]
            volumes = [np.random.randint(1000000, 5000000)]

            for day in range(1, n_days):
                # Random walk with drift and volatility
                daily_return = np.random.normal(0.0005, daily_volatility)
                new_price = prices[-1] * (1 + daily_return)
                prices.append(new_price)

                # Volume with some autocorrelation
                new_volume = max(100000, volumes[-1] * np.random.normal(1, 0.3))
                volumes.append(int(new_volume))

            # Create price data for each day
            for day_idx, (price, volume) in enumerate(zip(prices, volumes)):
                price_data.append(
                    {
                        "stock_id": stock_id,
                        "date": start_date + timedelta(days=day_idx),
                        "open": price * (1 + np.random.normal(0, 0.005)),
                        "high": price * (1 + abs(np.random.normal(0, 0.01))),
                        "low": price * (1 - abs(np.random.normal(0, 0.01))),
                        "close": price,
                        "volume": volume,
                        "daily_return": (
                            (price / prices[max(0, day_idx - 1)] - 1)
                            if day_idx > 0
                            else 0
                        ),
                    }
                )

        stocks_df = pd.DataFrame(stocks)
        price_data_df = pd.DataFrame(price_data)

        logger.info("✅ Financial data generation completed")
        return stocks_df, price_data_df

    def generate_restaurant_data(
        self, n_restaurants: int = 200, n_reviews: int = 10000, n_users: int = 3000
    ) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """
        Generate restaurant ratings and review data

        Args:
            n_restaurants: Number of restaurants to generate
            n_reviews: Number of reviews to generate
            n_users: Number of users to generate

        Returns:
            Tuple of (restaurants_df, users_df, reviews_df)
        """
        logger.info(
            f"Generating restaurant data: {n_restaurants} restaurants, {n_reviews} reviews, {n_users} users"
        )

        # Generate restaurants data
        restaurants = pd.DataFrame(
            {
                "restaurant_id": [f"REST{1000 + i}" for i in range(n_restaurants)],
                "name": [
                    f'{random.choice(["The", "Grand", "Little", "Royal", "Happy"])} {random.choice(["Bistro", "Cafe", "Grill", "House", "Place"])}'
                    for _ in range(n_restaurants)
                ],
                "cuisine_type": [
                    random.choice(self.restaurant_config["cuisines"])
                    for _ in range(n_restaurants)
                ],
                "price_range": [
                    random.choice(self.restaurant_config["price_ranges"])
                    for _ in range(n_restaurants)
                ],
                "location": [
                    f"Neighborhood {i % 10 + 1}" for i in range(n_restaurants)
                ],
                "avg_rating": np.round(
                    np.random.beta(5, 2, n_restaurants) * 2 + 3, 1
                ),  # Bias toward positive ratings
                "review_count": np.random.poisson(50, n_restaurants),
                "opening_year": np.random.randint(1990, 2023, n_restaurants),
            }
        )

        # Calculate price level from price range
        price_levels = {"$": 1, "$$": 2, "$$$": 3, "$$$$": 4}
        restaurants["price_level"] = restaurants["price_range"].map(price_levels)

        # Generate users data
        users = pd.DataFrame(
            {
                "user_id": [f"USER{5000 + i}" for i in range(n_users)],
                "join_date": [
                    datetime(2020, 1, 1) + timedelta(days=random.randint(0, 1460))
                    for _ in range(n_users)
                ],
                "location": [f"City {i % 15 + 1}" for i in range(n_users)],
                "review_count": np.random.poisson(15, n_users),
                "helpfulness_score": np.round(
                    np.random.beta(3, 2, n_users) * 5, 2
                ),  # Most users are helpful
            }
        )

        # Generate reviews data
        reviews = []

        for i in range(n_reviews):
            restaurant = random.choice(restaurants["restaurant_id"])
            restaurant_data = restaurants[
                restaurants["restaurant_id"] == restaurant
            ].iloc[0]
            cuisine = restaurant_data["cuisine_type"]
            base_rating = restaurant_data["avg_rating"]

            # Generate rating with some correlation to restaurant's average
            # But with individual variation
            rating_variation = np.random.normal(0, 0.8)  # Some users rate differently
            rating = np.clip(base_rating + rating_variation, 1, 5)
            rating = np.round(rating, 1)

            # Generate review text based on rating and cuisine
            review_template = random.choice(self.review_templates)
            dish = random.choice(self.dishes_by_cuisine.get(cuisine, ["the special"]))
            review_text = review_template.format(cuisine=cuisine, dish=dish)

            # Adjust review sentiment based on rating
            if rating <= 2:
                review_text = review_text.replace("Great", "Poor").replace(
                    "excellent", "terrible"
                )
                review_text = review_text.replace("Amazing", "Disappointing").replace(
                    "incredible", "awful"
                )
                review_text = review_text.replace("loved", "hated").replace(
                    "recommended", "not recommended"
                )

            reviews.append(
                {
                    "review_id": f"REV{100000 + i}",
                    "restaurant_id": restaurant,
                    "user_id": random.choice(users["user_id"]),
                    "rating": rating,
                    "review_text": review_text,
                    "review_date": datetime(2023, 1, 1)
                    + timedelta(days=random.randint(0, 365)),
                    "useful_count": np.random.poisson(
                        3
                    ),  # Some reviews get more useful votes
                    "service_rating": np.random.randint(1, 6),
                    "food_rating": np.random.randint(1, 6),
                    "ambiance_rating": np.random.randint(1, 6),
                    "value_rating": np.random.randint(1, 6),
                }
            )

        reviews_df = pd.DataFrame(reviews)

        logger.info("✅ Restaurant data generation completed")
        return restaurants, users, reviews_df

    def save_all_datasets(self, base_path: str = "data/raw"):
        """
        Generate and save all datasets for all projects

        Args:
            base_path: Base directory path to save datasets
        """
        logger.info(f"Saving all datasets to: {base_path}")

        projects = [
            "ecommerce",
            "healthcare",
            "banking",
            "hr",
            "fraud",
            "financial",
            "restaurant",
        ]

        # Create project directories
        for project in projects:
            project_path = Path(f"{base_path}/{project}")
            project_path.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created directory: {project_path}")

        try:
            # Generate and save e-commerce data
            customers, products, transactions = self.generate_ecommerce_data()
            customers.to_csv(f"{base_path}/ecommerce/customers.csv", index=False)
            products.to_csv(f"{base_path}/ecommerce/products.csv", index=False)
            transactions.to_csv(f"{base_path}/ecommerce/transactions.csv", index=False)
            logger.info("✅ E-commerce data saved")

            # Generate and save healthcare data
            patients, treatments, facilities = self.generate_healthcare_data()
            patients.to_csv(f"{base_path}/healthcare/patients.csv", index=False)
            treatments.to_csv(f"{base_path}/healthcare/treatments.csv", index=False)
            facilities.to_csv(f"{base_path}/healthcare/facilities.csv", index=False)
            logger.info("✅ Healthcare data saved")

            # Generate and save banking data
            bank_customers, bank_transactions = self.generate_banking_data()
            bank_customers.to_csv(f"{base_path}/banking/customers.csv", index=False)
            bank_transactions.to_csv(
                f"{base_path}/banking/transactions.csv", index=False
            )
            logger.info("✅ Banking data saved")

            # Generate and save HR data
            employees, exit_interviews = self.generate_hr_data()
            employees.to_csv(f"{base_path}/hr/employees.csv", index=False)
            exit_interviews.to_csv(f"{base_path}/hr/exit_interviews.csv", index=False)
            logger.info("✅ HR data saved")

            # Generate and save fraud detection data
            users, fraud_transactions = self.generate_fraud_data()
            users.to_csv(f"{base_path}/fraud/users.csv", index=False)
            fraud_transactions.to_csv(
                f"{base_path}/fraud/transactions.csv", index=False
            )
            logger.info("✅ Fraud detection data saved")

            # Generate and save financial data
            stocks, stock_prices = self.generate_financial_data()
            stocks.to_csv(f"{base_path}/financial/stocks.csv", index=False)
            stock_prices.to_csv(f"{base_path}/financial/prices.csv", index=False)
            logger.info("✅ Financial data saved")

            # Generate and save restaurant data
            restaurants, review_users, reviews = self.generate_restaurant_data()
            restaurants.to_csv(f"{base_path}/restaurant/restaurants.csv", index=False)
            review_users.to_csv(f"{base_path}/restaurant/users.csv", index=False)
            reviews.to_csv(f"{base_path}/restaurant/reviews.csv", index=False)
            logger.info("✅ Restaurant data saved")

            # Save dataset metadata
            self._save_dataset_metadata(base_path)

            logger.info("🎉 All datasets generated and saved successfully!")

        except Exception as e:
            logger.error(f"❌ Failed to save datasets: {e}")
            raise

    def _save_dataset_metadata(self, base_path: str):
        """Save metadata about generated datasets"""
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "seed": self.seed,
            "datasets": {
                "ecommerce": {
                    "customers": "Customer demographics and signup information",
                    "products": "Product catalog with pricing and categories",
                    "transactions": "Sales transactions with customer and product references",
                },
                "healthcare": {
                    "patients": "Patient medical records and admission data",
                    "treatments": "Medical treatments and outcomes",
                    "facilities": "Healthcare facility information",
                },
                "banking": {
                    "customers": "Bank customer profiles with churn indicators",
                    "transactions": "Banking transactions with fraud indicators",
                },
                "hr": {
                    "employees": "Employee demographics and work information",
                    "exit_interviews": "Exit interview data for employees who left",
                },
                "fraud": {
                    "users": "User account information",
                    "transactions": "Transaction data with fraud labels",
                },
                "financial": {
                    "stocks": "Stock metadata and company information",
                    "prices": "Daily stock price and volume data",
                },
                "restaurant": {
                    "restaurants": "Restaurant information and cuisine types",
                    "users": "User profiles for review system",
                    "reviews": "Restaurant reviews with ratings and text",
                },
            },
        }

        metadata_path = Path(f"{base_path}/dataset_metadata.json")
        with open(metadata_path, "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Dataset metadata saved: {metadata_path}")

    def get_dataset_info(self) -> Dict[str, Any]:
        """
        Get information about available datasets

        Returns:
            Dictionary with dataset information
        """
        return {
            "ecommerce": "E-commerce Sales Analysis - Customer transactions and product data",
            "healthcare": "Healthcare Patient Analytics - Medical records and treatment outcomes",
            "banking": "Bank Customer Churn Prediction - Customer profiles and transaction history",
            "hr": "HR Attrition Dashboard - Employee data and turnover analysis",
            "fraud": "Fraud Detection - Transaction data with fraud patterns",
            "financial": "Financial Stock Analysis - Stock prices and market data",
            "restaurant": "Restaurant Ratings & Review Analysis - Customer reviews and sentiment",
        }


# Convenience functions
def generate_all_data(seed: int = 42, base_path: str = "data/raw"):
    """
    Convenience function to generate all datasets

    Args:
        seed: Random seed for reproducible generation
        base_path: Base directory to save datasets
    """
    generator = MockDataGenerator(seed)
    generator.save_all_datasets(base_path)


def test_data_generation():
    """Test function to verify data generation works"""
    print("🧪 Testing Data Generation...")

    try:
        generator = MockDataGenerator(42)

        # Test each generator
        datasets = {
            "ecommerce": generator.generate_ecommerce_data(100, 20, 500),
            "healthcare": generator.generate_healthcare_data(200, 500, 10),
            "banking": generator.generate_banking_data(500, 2000),
            "hr": generator.generate_hr_data(300),
            "fraud": generator.generate_fraud_data(200, 1000),
            "financial": generator.generate_financial_data(10, 30),
            "restaurant": generator.generate_restaurant_data(50, 500, 200),
        }

        print("✅ All data generators working correctly!")

        # Print dataset sizes
        for project, data in datasets.items():
            if isinstance(data, tuple):
                sizes = [len(df) for df in data if isinstance(df, pd.DataFrame)]
                print(f"   {project}: {sizes}")
            else:
                print(f"   {project}: {len(data)} rows")

        return True

    except Exception as e:
        print(f"❌ Data generation test failed: {e}")
        return False


if __name__ == "__main__":
    # Test the data generator
    if test_data_generation():
        print("\n🎉 Data Generator is ready to use!")
        print("\n💡 Usage example:")
        print("   from shared.utils.data_generator import MockDataGenerator")
        print("   generator = MockDataGenerator(42)")
        print(
            "   customers, products, transactions = generator.generate_ecommerce_data()"
        )
        print("   generator.save_all_datasets('data/raw')")
    else:
        print("\n💡 There were issues with the data generator.")
