## 🚀 Complete Deployment and Automation
    
from sympy import python

#!/usr/bin/env python3\n",
"""
Deploy All Advanced Features
One-click setup for real-time data, ML models, sentiment analysis, and reporting
"""
import subprocess
import sys
import os
import time


def run_script(script_name, description):
    """Run a Python script with error handling"""
    print(f"\n🚀 {description}...")
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=True, text=True, cwd=os.path.dirname(__file__))
        if result.returncode == 0:
            print(f"✅ {description} completed successfully!")
            return True
        else:
            print(f"❌ {description} failed:")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Error running {script_name}: {e}")
        return False

def main():
    """Deploy all advanced features"""
    print("🎯 DEPLOYING ADVANCED FINANCIAL ANALYSIS FEATURES")
    print("=" * 60)

    scripts_to_run = [
        ("real_time_data.py", "Real-time Data Integration with Yahoo Finance"),
        ("sentiment_analysis.py", "Financial News Sentiment Analysis"),
        ("ml_model_deployment.py", "Machine Learning Model Deployment"),
        ("automated_reporting.py", "Automated Reporting System"),
    ]
    
    success_count = 0
    
    for script, description in scripts_to_run:
        if run_script(script, description):
            success_count += 1
        time.sleep(2)  # Brief pause between scripts
    
    print("\n" + "=" * 60)
    print(f"📊 Deployment Summary: {success_count}/{len(scripts_to_run)} features deployed\n")
    
    if success_count == len(scripts_to_run):
        print("🎉 All advanced features deployed successfully!")
        print("\n🔧 Next Steps:")
        print("1. Run the LSTM notebook: jupyter lab notebooks/04_lstm_prediction.ipynb")
        print("2. Configure cloud deployment using the provided Docker files")
        print("3. Set up cron jobs for automated reporting")
        print("4. Customize email alerts in automated_reporting.py")
    else:
        print("⚠️  Some features failed. Check the errors above.")

if __name__ == "__main__":
    main()