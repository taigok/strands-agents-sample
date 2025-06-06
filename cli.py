#!/usr/bin/env python3
"""
CLI script for testing the Strands Multi-Agent System
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

from src.agents import CoordinatorAgent, DataAnalystAgent, ResearchAgent, ReportGeneratorAgent
from src.config.settings import settings


def test_data_analysis(file_path: str):
    """Test data analysis functionality"""
    print(f"🔍 Testing Data Analysis with file: {file_path}")
    
    try:
        agent = DataAnalystAgent()
        result = agent.analyze_file(file_path, "comprehensive")
        
        print("✅ Data analysis completed successfully!")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error in data analysis: {e}")
        return False
    
    return True


def test_research(query: str):
    """Test research functionality"""
    print(f"🌐 Testing Research with query: {query}")
    
    try:
        agent = ResearchAgent()
        result = agent.conduct_market_research(
            topic=query,
            aspects=["Market Size", "Key Players", "Trends"],
            num_sources=5
        )
        
        print("✅ Research completed successfully!")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error in research: {e}")
        return False
    
    return True


def test_report_generation(title: str):
    """Test report generation functionality"""
    print(f"📝 Testing Report Generation: {title}")
    
    try:
        agent = ReportGeneratorAgent()
        
        # Sample content for report
        sample_content = {
            "analysis": "Sample analysis results",
            "research": "Sample research findings",
            "metrics": {"revenue": 1000000, "growth": 15}
        }
        
        result = agent.create_executive_summary(
            full_content=sample_content,
            max_pages=2
        )
        
        print("✅ Report generation completed successfully!")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error in report generation: {e}")
        return False
    
    return True


def test_coordinator(request: str):
    """Test coordinator functionality"""
    print(f"🎯 Testing Coordinator with request: {request}")
    
    try:
        agent = CoordinatorAgent()
        result = agent.execute_workflow(request)
        
        print("✅ Coordinator workflow completed successfully!")
        print(json.dumps(result, indent=2, default=str))
        
    except Exception as e:
        print(f"❌ Error in coordinator: {e}")
        return False
    
    return True


def run_all_tests():
    """Run all agent tests"""
    print("🚀 Running all agent tests...\n")
    
    tests = [
        ("Data Analysis", lambda: test_data_analysis("sample_data.csv")),
        ("Research", lambda: test_research("AI market trends")),
        ("Report Generation", lambda: test_report_generation("Test Report")),
        ("Coordinator", lambda: test_coordinator("Analyze market trends and create a report"))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*50}")
        print(f"Testing: {test_name}")
        print('='*50)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print(f"\n{'='*50}")
    print("TEST RESULTS SUMMARY")
    print('='*50)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, success in results if success)
    print(f"\nTotal: {total_passed}/{len(results)} tests passed")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="CLI for testing Strands Multi-Agent System"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Data analysis command
    data_parser = subparsers.add_parser('analyze', help='Test data analysis')
    data_parser.add_argument('file_path', help='Path to data file')
    
    # Research command
    research_parser = subparsers.add_parser('research', help='Test research')
    research_parser.add_argument('query', help='Research query')
    
    # Report command
    report_parser = subparsers.add_parser('report', help='Test report generation')
    report_parser.add_argument('title', help='Report title')
    
    # Coordinator command
    coord_parser = subparsers.add_parser('coordinate', help='Test coordinator')
    coord_parser.add_argument('request', help='Coordination request')
    
    # Test all command
    subparsers.add_parser('test-all', help='Run all tests')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print(f"🤖 Strands Multi-Agent System CLI")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Environment: {settings.environment}")
    print(f"Model: {settings.bedrock_model_id}")
    print()
    
    if args.command == 'analyze':
        if not Path(args.file_path).exists():
            print(f"❌ File not found: {args.file_path}")
            sys.exit(1)
        test_data_analysis(args.file_path)
    
    elif args.command == 'research':
        test_research(args.query)
    
    elif args.command == 'report':
        test_report_generation(args.title)
    
    elif args.command == 'coordinate':
        test_coordinator(args.request)
    
    elif args.command == 'test-all':
        run_all_tests()
    
    elif args.command == 'status':
        print("📊 System Status:")
        print(f"  AWS Region: {settings.aws_region}")
        print(f"  Model: {settings.bedrock_model_id}")
        print(f"  Max Iterations: {settings.agent_max_iterations}")
        print(f"  Timeout: {settings.agent_timeout_seconds}s")
        print(f"  Tracing: {'Enabled' if settings.enable_tracing else 'Disabled'}")
        print(f"  Log Level: {settings.log_level}")


if __name__ == "__main__":
    main()