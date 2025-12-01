"""
Database Configuration Module
Handles database connections, connection pooling, and environment-specific configurations
"""

import os
import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DatabaseConfig:
    """Database configuration with environment support and connection pooling"""

    # Environment-based configuration
    ENVIRONMENTS = {
        "development": {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "portfolio_dev"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "postgres"),  # Default for dev only
            "port": os.getenv("DB_PORT", "5432"),
            "pool_size": 5,
            "max_overflow": 10,
        },
        "production": {
            "host": os.getenv("DB_HOST", "localhost"),
            "database": os.getenv("DB_NAME", "portfolio_prod"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", ""),  # MUST be set via environment
            "port": os.getenv("DB_PORT", "5432"),
            "pool_size": 10,
            "max_overflow": 20,
        },
        "test": {
            "host": "localhost",
            "database": "portfolio_test",
            "user": "postgres",
            "password": "postgres",
            "port": "5432",
            "pool_size": 2,
            "max_overflow": 5,
        },
    }

    def __init__(self, environment="development"):
        self.environment = environment
        self.config = self.ENVIRONMENTS.get(
            environment, self.ENVIRONMENTS["development"]
        )
        self.engine = None
        self.SessionLocal = None
        self.Base = declarative_base()

    def get_connection_string(self, driver="psycopg2"):
        """Get connection string for the current environment"""
        config = self.config
        if driver == "psycopg2":
            return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"
        elif driver == "sqlalchemy":
            return f"postgresql+psycopg2://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"

    def init_engine(self):
        """Initialize SQLAlchemy engine with connection pooling"""
        try:
            connection_string = self.get_connection_string("sqlalchemy")
            self.engine = create_engine(
                connection_string,
                poolclass=QueuePool,
                pool_size=self.config["pool_size"],
                max_overflow=self.config["max_overflow"],
                pool_pre_ping=True,  # Verify connections before using them
                echo=False,  # Set to True for SQL query logging
            )
            self.SessionLocal = sessionmaker(
                autocommit=False, autoflush=False, bind=self.engine
            )
            logger.info(
                f"Database engine initialized for {self.environment} environment"
            )
            return self.engine
        except Exception as e:
            logger.error(f"Failed to initialize database engine: {e}")
            raise

    def get_engine(self):
        """Get or initialize the database engine"""
        if self.engine is None:
            return self.init_engine()
        return self.engine

    def get_session(self):
        """Get a new database session"""
        if self.SessionLocal is None:
            self.init_engine()
        return self.SessionLocal()

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations"""
        session = self.get_session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    def get_raw_connection(self):
        """Get raw psycopg2 connection for SQL execution"""
        try:
            connection = psycopg2.connect(
                **{
                    "host": self.config["host"],
                    "database": self.config["database"],
                    "user": self.config["user"],
                    "password": self.config["password"],
                    "port": self.config["port"],
                }
            )
            return connection
        except Exception as e:
            logger.error(f"Failed to establish raw database connection: {e}")
            raise

    def test_connection(self):
        """Test database connection"""
        try:
            from sqlalchemy import text

            with self.session_scope() as session:
                session.execute(text("SELECT 1"))
            logger.info("Database connection test successful")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def create_tables(self, metadata):
        """Create all tables from metadata"""
        try:
            metadata.create_all(bind=self.get_engine())
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise


# Global database instance
db_config = DatabaseConfig()


# Convenience functions
def get_db():
    """Dependency for FastAPI-style applications"""
    db = db_config.get_session()
    try:
        yield db
    finally:
        db.close()


def get_engine():
    return db_config.get_engine()


def get_connection_string():
    return db_config.get_connection_string()


def test_database_connection():
    return db_config.test_connection()


if __name__ == "__main__":
    # Test the configuration
    print("Testing database configuration...")
    print(f"Connection string: {get_connection_string()}")

    if test_database_connection():
        print("✅ Database connection successful!")
    else:
        print("❌ Database connection failed!")
