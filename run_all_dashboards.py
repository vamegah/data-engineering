
#!/usr/bin/env python3
"""
Data Engineering Portfolio - Dashboard Manager

This script helps manage and run Streamlit dashboards for all projects.
Run individual dashboards or get instructions for running multiple dashboards.
"""

import os
import sys
import subprocess
import webbrowser
import threading
import time
from pathlib import Path

class DashboardManager:
    def __init__(self):
        self.dashboards = {
            'ecommerce': {
                'path': 'ecommerce/dashboards/streamlit_app.py',
                'name': 'E-commerce Sales Dashboard',
                'port': 8501,
                'description': 'Sales analytics and customer insights'
            },
            'healthcare': {
                'path': 'healthcare/dashboards/streamlit_app.py', 
                'name': 'Healthcare Analytics Dashboard',
                'port': 8502,
                'description': 'Patient outcomes and facility performance'
            },
            'banking': {
                'path': 'banking/dashboards/streamlit_app.py',
                'name': 'Banking Churn Dashboard',
                'port': 8503,
                'description': 'Customer retention and risk analysis'
            },
            'hr': {
                'path': 'hr/dashboards/streamlit_app.py',
                'name': 'HR Analytics Dashboard',
                'port': 8504,
                'description': 'Employee attrition and workforce analytics'
            },
            'fraud': {
                'path': 'fraud/dashboards/streamlit_app.py',
                'name': 'Fraud Detection Dashboard',
                'port': 8505,
                'description': 'Anomaly detection and pattern analysis'
            },
            'financial': {
                'path': 'financial/dashboards/streamlit_app.py',
                'name': 'Financial Analysis Dashboard', 
                'port': 8506,
                'description': 'Stock market trends and portfolio analysis'
            },
            'restaurant': {
                'path': 'restaurant/dashboards/streamlit_app.py',
                'name': 'Restaurant Reviews Dashboard',
                'port': 8507,
                'description': 'Customer sentiment and business insights'
            }
        }
    
    def check_dashboard_exists(self, dashboard_key):
        """Check if dashboard file exists"""
        dashboard_info = self.dashboards.get(dashboard_key)
        if not dashboard_info:
            return False
        
        return Path(dashboard_info['path']).exists()
    
    def list_dashboards(self):
        """List all available dashboards"""
        print("\n📊 AVAILABLE DASHBOARDS")
        print("=" * 60)
        
        for i, (key, info) in enumerate(self.dashboards.items(), 1):
            exists = self.check_dashboard_exists(key)
            status = "✅ Ready" if exists else "❌ Not Found"
            print(f"{i}. {info['name']}")
            print(f"   📍 Port: {info['port']} | {info['description']}")
            print(f"   📁 Path: {info['path']}")
            print(f"   🚦 Status: {status}")
            print()
    
    def run_single_dashboard(self, dashboard_key, open_browser=True):
        """Run a single dashboard"""
        if not self.check_dashboard_exists(dashboard_key):
            print(f"❌ Dashboard not found: {self.dashboards[dashboard_key]['path']}")
            return False
        
        dashboard_info = self.dashboards[dashboard_key]
        
        print(f"🚀 Starting {dashboard_info['name']}...")
        print(f"📍 Dashboard will be available at: http://localhost:{dashboard_info['port']}")
        print(f"📊 Description: {dashboard_info['description']}")
        print("⏹️  Press Ctrl+C to stop the dashboard")
        print("-" * 50)
        
        # Open browser after a short delay
        if open_browser:
            def open_browser_tab():
                time.sleep(3)  # Wait for dashboard to start
                webbrowser.open(f"http://localhost:{dashboard_info['port']}")
            
            browser_thread = threading.Thread(target=open_browser_tab)
            browser_thread.daemon = True
            browser_thread.start()
        
        try:
            # Run the Streamlit app
            subprocess.run([
                sys.executable, "-m", "streamlit", "run", 
                dashboard_info['path'],
                "--server.port", str(dashboard_info['port']),
                "--server.headless", "false",
                "--browser.gatherUsageStats", "false"
            ])
            return True
        except KeyboardInterrupt:
            print(f"\n⏹️  Stopped {dashboard_info['name']}")
            return True
        except Exception as e:
            print(f"❌ Error running dashboard: {e}")
            return False
    
    def show_quick_commands(self):
        """Show quick commands for running dashboards"""
        print("\n🎮 QUICK START COMMANDS")
        print("=" * 40)
        
        for key, info in self.dashboards.items():
            cmd = f"streamlit run {info['path']} --server.port {info['port']}"
            print(f"📍 {info['name']}:")
            print(f"   {cmd}")
            print()
    
    def run_interactive_mode(self):
        """Run in interactive mode to let user choose dashboard"""
        self.list_dashboards()
        
        print("🎯 INTERACTIVE MODE")
        print("=" * 40)
        
        while True:
            print("\nOptions:")
            print("1-7: Run specific dashboard")
            print("c: Show quick commands") 
            print("l: List dashboards again")
            print("q: Quit")
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == 'c':
                self.show_quick_commands()
            elif choice == 'l':
                self.list_dashboards()
            elif choice in ['1', '2', '3', '4', '5', '6', '7']:
                dashboard_keys = list(self.dashboards.keys())
                selected_key = dashboard_keys[int(choice) - 1]
                self.run_single_dashboard(selected_key)
            else:
                print("❌ Invalid choice. Please try again.")
    
    def create_dashboard_template(self, project_name):
        """Create a basic dashboard template for a project"""
        template = f'''import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Page configuration
st.set_page_config(
    page_title="{project_name.title()} Dashboard",
    page_icon="📊",
    layout="wide"
)

# Title
st.title("{project_name.title()} Analytics Dashboard")
st.markmary("Interactive dashboard for data analysis and visualization")

# Load data function
@st.cache_data
def load_data():
    """Load project data"""
    try:
        # Example: Load your data here
        # df = pd.read_csv('data/raw/your_data.csv')
        return None
    except Exception as e:
        st.error(f"Error loading data: {{e}}")
        return None

# Sidebar
st.sidebar.header("Filters & Controls")
st.sidebar.info("Configure your analysis settings here")

# Main content
st.header("Key Metrics")

# Placeholder metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Records", "1,000", "10%")

with col2:
    st.metric("Success Rate", "85%", "2%")

with col3:
    st.metric("Growth", "12%", "3%")

with col4:
    st.metric("Performance", "92%", "-1%")

# Data visualization section
st.header("Data Analysis")

tab1, tab2, tab3 = st.tabs(["Overview", "Trends", "Insights"])

with tab1:
    st.subheader("Data Overview")
    st.info("Add your data overview visualizations here")

with tab2:
    st.subheader("Trend Analysis") 
    st.info("Add your time series and trend analysis here")

with tab3:
    st.subheader("Business Insights")
    st.info("Add your key insights and recommendations here")

# Footer
st.markdown("---")
st.markdown("Built with Streamlit | Data Engineering Portfolio")
'''

        dashboard_path = f"{project_name}/dashboards/app.py"
        Path(dashboard_path).parent.mkdir(parents=True, exist_ok=True)
        
        with open(dashboard_path, 'w') as f:
            f.write(template)
        
        print(f"✅ Created dashboard template: {dashboard_path}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Manage Portfolio Dashboards')
    parser.add_argument('dashboard', nargs='?', 
                       choices=['ecommerce', 'healthcare', 'banking', 'hr', 'fraud', 'financial', 'restaurant', 'list', 'interactive'],
                       help='Dashboard to run or "list" to show all, "interactive" for menu')
    parser.add_argument('--no-browser', action='store_true',
                       help='Don\'t open browser automatically')
    parser.add_argument('--create-template', 
                       choices=['ecommerce', 'healthcare', 'banking', 'hr', 'fraud', 'financial', 'restaurant'],
                       help='Create a dashboard template for a project')
    
    args = parser.parse_args()
    
    manager = DashboardManager()
    
    if args.create_template:
        manager.create_dashboard_template(args.create_template)
        return
    
    if not args.dashboard or args.dashboard == 'list':
        manager.list_dashboards()
        manager.show_quick_commands()
    elif args.dashboard == 'interactive':
        manager.run_interactive_mode()
    else:
        manager.run_single_dashboard(args.dashboard, not args.no_browser)

if __name__ == "__main__":
    main()