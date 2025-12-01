"""
Setup script for production environment configuration.
"""

import os
import shutil
from pathlib import Path


def setup_production_environment():
    """Set up production environment configuration."""

    banking_dir = Path(__file__).parent

    # 1. Create .env file if it doesn't exist
    env_file = banking_dir / ".env"
    env_example = banking_dir / ".env.example"

    if not env_file.exists() and env_example.exists():
        shutil.copy(env_example, env_file)
        print("✅ Created .env file from .env.example")
        print("⚠️  Please update the .env file with your actual credentials")
    elif env_file.exists():
        print("ℹ️  .env file already exists")
    else:
        print("❌ .env.example not found")

    # 2. Create necessary directories
    directories = [
        banking_dir / "api",
        banking_dir / "airflow" / "dags",
        banking_dir / "logs",
        banking_dir / "models",
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
        print(f"✅ Ensured directory exists: {directory.name}")

    # 3. Create __init__.py files
    init_files = [
        banking_dir / "api" / "__init__.py",
        banking_dir / "airflow" / "__init__.py",
        banking_dir / "airflow" / "dags" / "__init__.py",
    ]

    for init_file in init_files:
        if not init_file.exists():
            init_file.write_text("")
            print(f"✅ Created {init_file.relative_to(banking_dir)}")

    # 4. Check for required model files
    model_file = banking_dir / "models" / "churn_model.pkl"
    if not model_file.exists():
        print("⚠️  Model file not found at models/churn_model.pkl")
        print("   Run the Jupyter notebooks to train and save the model")

    # 5. Print next steps
    print("\n" + "=" * 60)
    print("🎉 Production environment setup complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Update .env with your database credentials")
    print("2. Train the model by running the notebooks:")
    print("   - 01_data_cleaning.ipynb")
    print("   - 02_eda.ipynb")
    print("   - 03_churn_prediction.ipynb")
    print("3. Run tests: pytest tests/test_banking.py -v")
    print("4. Start the API: python banking/api/app.py")
    print("5. Or use Docker: docker-compose up -d")
    print("\n📖 See banking/IMPLEMENTATION_SUMMARY.md for detailed instructions")


if __name__ == "__main__":
    setup_production_environment()
