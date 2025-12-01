#!/usr/bin/env python3
"""
Quick deployment test script
Tests that all services can start and respond to health checks
"""

import subprocess
import time
import requests
import sys

def print_header(text):
    print(f"\n{'='*60}")
    print(f"  {text}")
    print(f"{'='*60}\n")

def check_docker():
    """Check if Docker is available"""
    try:
        subprocess.run(["docker", "--version"], check=True, capture_output=True)
        print("✅ Docker is installed")
        return True
    except:
        print("❌ Docker is not installed or not running")
        return False

def start_services():
    """Start all services using docker-compose"""
    print_header("Starting Services")
    
    try:
        print("Building and starting containers...")
        subprocess.run(["docker-compose", "up", "-d", "--build"], check=True)
        print("✅ Services started successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to start services: {e}")
        return False

def wait_for_services(timeout=120):
    """Wait for services to be ready"""
    print_header("Waiting for Services")
    
    services = {
        "Fraud API": "http://localhost/api/fraud/health",
        "E-commerce API": "http://localhost/api/ecommerce/health",
        "Financial API": "http://localhost/api/financial/health",
        "Healthcare API": "http://localhost/api/healthcare/health",
        "HR API": "http://localhost/api/hr/health",
        "Restaurant API": "http://localhost/api/restaurant/health",
    }
    
    start_time = time.time()
    ready_services = set()
    
    print(f"Waiting up to {timeout} seconds for all services to be ready...\n")
    
    while time.time() - start_time < timeout:
        for name, url in services.items():
            if name not in ready_services:
                try:
                    response = requests.get(url, timeout=2)
                    if response.status_code == 200:
                        print(f"✅ {name} is ready")
                        ready_services.add(name)
                except:
                    pass
        
        if len(ready_services) == len(services):
            print(f"\n🎉 All services are ready!")
            return True
        
        time.sleep(2)
    
    print(f"\n⚠️ Timeout after {timeout} seconds")
    print(f"Ready: {len(ready_services)}/{len(services)}")
    return False

def test_endpoints():
    """Test key endpoints"""
    print_header("Testing Endpoints")
    
    tests = [
        ("Main Page", "http://localhost/"),
        ("Fraud API Docs", "http://localhost/api/fraud/docs"),
        ("E-commerce API Docs", "http://localhost/api/ecommerce/docs"),
        ("Financial API Docs", "http://localhost/api/financial/docs"),
        ("Healthcare API Docs", "http://localhost/api/healthcare/docs"),
        ("HR API Docs", "http://localhost/api/hr/docs"),
        ("Restaurant API Docs", "http://localhost/api/restaurant/docs"),
    ]
    
    results = []
    for name, url in tests:
        try:
            response = requests.get(url, timeout=5)
            status = "✅" if response.status_code == 200 else "⚠️"
            print(f"{status} {name}: {response.status_code}")
            results.append(response.status_code == 200)
        except Exception as e:
            print(f"❌ {name}: Failed ({str(e)[:50]})")
            results.append(False)
    
    success_rate = sum(results) / len(results) * 100
    print(f"\n📊 Success Rate: {success_rate:.0f}% ({sum(results)}/{len(results)})")
    
    return success_rate >= 80

def show_urls():
    """Display access URLs"""
    print_header("Access URLs")
    
    print("🌐 Main Dashboard:")
    print("   http://localhost\n")
    
    print("📚 API Documentation:")
    print("   • Fraud Detection:  http://localhost/api/fraud/docs")
    print("   • E-commerce:       http://localhost/api/ecommerce/docs")
    print("   • Financial:        http://localhost/api/financial/docs")
    print("   • Healthcare:       http://localhost/api/healthcare/docs")
    print("   • HR Analytics:     http://localhost/api/hr/docs")
    print("   • Restaurant:       http://localhost/api/restaurant/docs")
    
def show_commands():
    """Display useful commands"""
    print_header("Useful Commands")
    
    print("View logs:")
    print("   docker-compose logs -f")
    print("\nStop services:")
    print("   docker-compose down")
    print("\nRestart a service:")
    print("   docker-compose restart fraud-api")
    print("\nCheck status:")
    print("   docker-compose ps")

def main():
    """Main deployment test"""
    print_header("🚀 Portfolio Deployment Test")
    
    # Check prerequisites
    if not check_docker():
        print("\n❌ Please install Docker first:")
        print("   https://docs.docker.com/get-docker/")
        sys.exit(1)
    
    # Start services
    if not start_services():
        print("\n❌ Failed to start services")
        sys.exit(1)
    
    # Wait for services
    print("\nGiving services time to initialize...")
    time.sleep(10)
    
    if not wait_for_services():
        print("\n⚠️ Some services may not be ready yet")
        print("   Try waiting a bit longer or check logs:")
        print("   docker-compose logs")
    
    # Test endpoints
    if test_endpoints():
        print("\n✅ Deployment test successful!")
    else:
        print("\n⚠️ Some endpoints are not responding")
    
    # Show information
    show_urls()
    show_commands()
    
    print_header("🎉 Deployment Complete!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
