#!/usr/bin/env python3
"""
Database Setup Script
Creates database schema, tables, and initial setup for all projects
"""

import sys
import os
import logging
from pathlib import Path

# Add shared modules to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from config.database import DatabaseConfig, db_config
from utils.helpers import logger


class DatabaseSetup:
    """Database setup and initialization"""

    def __init__(self, environment="development"):
        self.db_config = DatabaseConfig(environment)
        self.environment = environment

    def create_database_schema(self):
        """Create the main database schema"""
        try:
            with self.db_config.get_raw_connection() as conn:
                with conn.cursor() as cur:
                    # Create schema if not exists
                    cur.execute("CREATE SCHEMA IF NOT EXISTS portfolio;")

                    # Set search path
                    cur.execute("SET search_path TO portfolio, public;")

                    # Create extension for additional functionality
                    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

                    conn.commit()
                    logger.info("Database schema created successfully")

        except Exception as e:
            logger.error(f"Failed to create database schema: {e}")
            raise

    def create_ecommerce_tables(self):
        """Create tables for ecommerce project"""
        try:
            with self.db_config.get_raw_connection() as conn:
                with conn.cursor() as cur:
                    # Customers table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.customers (
                            customer_id VARCHAR(50) PRIMARY KEY,
                            signup_date DATE,
                            location VARCHAR(100),
                            tier VARCHAR(50),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    # Products table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.products (
                            product_id VARCHAR(50) PRIMARY KEY,
                            product_name VARCHAR(200),
                            category VARCHAR(100),
                            price DECIMAL(10,2),
                            cost DECIMAL(10,2),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    # Transactions table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.transactions (
                            transaction_id VARCHAR(50) PRIMARY KEY,
                            customer_id VARCHAR(50) REFERENCES portfolio.customers(customer_id),
                            product_id VARCHAR(50) REFERENCES portfolio.products(product_id),
                            date DATE,
                            quantity INTEGER,
                            region VARCHAR(50),
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    conn.commit()
                    logger.info("E-commerce tables created successfully")

        except Exception as e:
            logger.error(f"Failed to create e-commerce tables: {e}")
            raise

    def create_healthcare_tables(self):
        """Create tables for healthcare project"""
        try:
            with self.db_config.get_raw_connection() as conn:
                with conn.cursor() as cur:
                    # Facilities table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.facilities (
                            facility_id VARCHAR(50) PRIMARY KEY,
                            facility_name VARCHAR(200),
                            facility_type VARCHAR(100),
                            specialty VARCHAR(100),
                            location VARCHAR(100),
                            bed_capacity INTEGER,
                            established_year INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    # Patients table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.patients (
                            patient_id VARCHAR(50) PRIMARY KEY,
                            age INTEGER,
                            gender VARCHAR(20),
                            blood_type VARCHAR(5),
                            primary_condition VARCHAR(100),
                            admission_date DATE,
                            discharge_date DATE,
                            facility_id VARCHAR(50) REFERENCES portfolio.facilities(facility_id),
                            insurance_type VARCHAR(50),
                            readmission_30_days INTEGER,
                            length_of_stay INTEGER GENERATED ALWAYS AS (discharge_date - admission_date) STORED,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    # Treatments table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.treatments (
                            treatment_id VARCHAR(50) PRIMARY KEY,
                            patient_id VARCHAR(50) REFERENCES portfolio.patients(patient_id),
                            treatment_type VARCHAR(100),
                            treatment_date DATE,
                            cost DECIMAL(10,2),
                            duration_days INTEGER,
                            outcome VARCHAR(50),
                            medication_prescribed BOOLEAN,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    conn.commit()
                    logger.info("Healthcare tables created successfully")

        except Exception as e:
            logger.error(f"Failed to create healthcare tables: {e}")
            raise

    def create_banking_tables(self):
        """Create tables for banking project"""
        try:
            with self.db_config.get_raw_connection() as conn:
                with conn.cursor() as cur:
                    # Banking customers table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.banking_customers (
                            customer_id VARCHAR(50) PRIMARY KEY,
                            credit_score INTEGER,
                            country VARCHAR(50),
                            gender VARCHAR(20),
                            age INTEGER,
                            tenure INTEGER,
                            balance DECIMAL(15,2),
                            products_number INTEGER,
                            credit_card INTEGER,
                            active_member INTEGER,
                            estimated_salary DECIMAL(15,2),
                            churn INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    # Banking transactions table
                    cur.execute(
                        """
                        CREATE TABLE IF NOT EXISTS portfolio.banking_transactions (
                            transaction_id VARCHAR(50) PRIMARY KEY,
                            customer_id VARCHAR(50) REFERENCES portfolio.banking_customers(customer_id),
                            transaction_type VARCHAR(50),
                            amount DECIMAL(15,2),
                            date DATE,
                            merchant VARCHAR(100),
                            location VARCHAR(50),
                            is_fraudulent INTEGER,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        );
                    """
                    )

                    conn.commit()
                    logger.info("Banking tables created successfully")

        except Exception as e:
            logger.error(f"Failed to create banking tables: {e}")
            raise

    def create_indexes(self):
        """Create performance indexes"""
        try:
            with self.db_config.get_raw_connection() as conn:
                with conn.cursor() as cur:

                    # E-commerce indexes
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_transactions_date ON portfolio.transactions(date);"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_transactions_customer ON portfolio.transactions(customer_id);"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_transactions_region ON portfolio.transactions(region);"
                    )

                    # Healthcare indexes
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_patients_admission ON portfolio.patients(admission_date);"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_patients_facility ON portfolio.patients(facility_id);"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_treatments_patient ON portfolio.treatments(patient_id);"
                    )

                    # Banking indexes
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_banking_tx_date ON portfolio.banking_transactions(date);"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_banking_tx_customer ON portfolio.banking_transactions(customer_id);"
                    )
                    cur.execute(
                        "CREATE INDEX IF NOT EXISTS idx_banking_tx_type ON portfolio.banking_transactions(transaction_type);"
                    )

                    conn.commit()
                    logger.info("Database indexes created successfully")

        except Exception as e:
            logger.error(f"Failed to create indexes: {e}")
            raise

    def setup_complete_database(self):
        """Complete database setup for all projects"""
        try:
            logger.info(
                f"Starting database setup for {self.environment} environment..."
            )

            # Test connection first
            if not self.db_config.test_connection():
                raise Exception("Database connection test failed")

            # Create schema
            self.create_database_schema()

            # Create project tables
            self.create_ecommerce_tables()
            self.create_healthcare_tables()
            self.create_banking_tables()

            # Create indexes
            self.create_indexes()

            logger.info("✅ Database setup completed successfully!")
            return True

        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
            return False

    def get_table_info(self):
        """Get information about created tables"""
        try:
            with self.db_config.get_raw_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        SELECT table_name, table_type 
                        FROM information_schema.tables 
                        WHERE table_schema = 'portfolio'
                        ORDER BY table_name;
                    """
                    )
                    tables = cur.fetchall()

                    print("\n📊 Database Tables in Portfolio Schema:")
                    print("-" * 50)
                    for table in tables:
                        print(f"  {table[0]} ({table[1]})")
                    print("-" * 50)

                    return tables

        except Exception as e:
            logger.error(f"Failed to get table info: {e}")
            return []


def main():
    """Main function to run database setup"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Setup database for data engineering portfolio"
    )
    parser.add_argument(
        "--env",
        choices=["development", "production", "test"],
        default="development",
        help="Environment to setup",
    )
    parser.add_argument(
        "--list-tables", action="store_true", help="List existing tables"
    )

    args = parser.parse_args()

    setup = DatabaseSetup(args.env)

    if args.list_tables:
        setup.get_table_info()
    else:
        success = setup.setup_complete_database()
        if success:
            setup.get_table_info()
        else:
            sys.exit(1)


if __name__ == "__main__":
    main()
