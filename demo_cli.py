#!/usr/bin/env python3
"""
Demo CLI for testing the Strands Multi-Agent System
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime

from demo_agents import MockCoordinatorAgent


def test_data_analysis(file_path: str):
    """Test data analysis functionality"""
    print(f"🔍 Testing Data Analysis with file: {file_path}")
    
    if not Path(file_path).exists():
        print(f"❌ File not found: {file_path}")
        return False
    
    try:
        coordinator = MockCoordinatorAgent()
        result = coordinator.data_analyst.analyze_file(file_path, "comprehensive")
        
        print("✅ Data analysis completed successfully!")
        
        # Show key results
        if result['status'] == 'completed':
            analysis = result.get('analysis', {})
            file_info = analysis.get('file_info', {})
            insights = analysis.get('insights', [])
            
            print(f"\n📊 Analysis Summary:")
            print(f"   File: {file_info.get('shape', 'N/A')} (rows × columns)")
            print(f"   Columns: {', '.join(file_info.get('columns', []))}")
            print(f"   Insights: {len(insights)} key findings")
            
            print(f"\n🔍 Key Insights:")
            for i, insight in enumerate(insights[:5], 1):
                print(f"   {i}. {insight}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in data analysis: {e}")
        return False


def test_research(query: str):
    """Test research functionality"""
    print(f"🌐 Testing Research with query: {query}")
    
    try:
        coordinator = MockCoordinatorAgent()
        result = coordinator.research_agent.conduct_market_research(
            topic=query,
            aspects=["Market Size", "Key Players", "Trends"],
            num_sources=5
        )
        
        print("✅ Research completed successfully!")
        
        if result['status'] == 'completed':
            research = result.get('research', {})
            findings = research.get('findings', {})
            insights = research.get('overall_insights', [])
            
            print(f"\n📈 Research Summary:")
            print(f"   Topic: {research.get('topic', 'N/A')}")
            print(f"   Aspects: {len(findings)} areas analyzed")
            print(f"   Sources: {research.get('sources_consulted', 0)} consulted")
            
            print(f"\n🔍 Key Findings:")
            for aspect, finding in findings.items():
                print(f"   {aspect}: {finding.get('summary', 'No summary')}")
            
            print(f"\n💡 Overall Insights:")
            for i, insight in enumerate(insights[:3], 1):
                print(f"   {i}. {insight}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in research: {e}")
        return False


def test_report_generation(title: str):
    """Test report generation functionality"""
    print(f"📝 Testing Report Generation: {title}")
    
    try:
        coordinator = MockCoordinatorAgent()
        
        # Sample content for report
        sample_data_insights = {
            "status": "completed",
            "analysis": {
                "file_info": {"shape": [100, 5], "columns": ["date", "sales", "region"]},
                "insights": ["Sales show 15% growth", "North region outperforms others"]
            }
        }
        
        sample_research_findings = {
            "status": "completed",
            "research": {
                "topic": title,
                "findings": {"Market Size": {"summary": "Growing rapidly"}},
                "overall_insights": ["Strong market potential", "Competitive landscape"]
            }
        }
        
        result = coordinator.report_generator.create_comprehensive_report(
            title=title,
            data_insights=sample_data_insights,
            research_findings=sample_research_findings
        )
        
        print("✅ Report generation completed successfully!")
        
        if result['status'] == 'completed':
            report = result.get('report', {})
            sections = report.get('sections', {})
            
            print(f"\n📄 Report Summary:")
            print(f"   Title: {report.get('title', 'N/A')}")
            print(f"   Sections: {len(sections)} generated")
            print(f"   Generated: {report.get('generated_at', 'N/A')}")
            
            print(f"\n📋 Sections Created:")
            for section_key, section in sections.items():
                title = section.get('title', section_key)
                content_preview = section.get('content', '')[:100] + "..."
                print(f"   • {title}: {content_preview}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in report generation: {e}")
        return False


def test_full_workflow(request: str, data_file: str = None):
    """Test complete multi-agent workflow"""
    print(f"🎯 Testing Complete Workflow")
    print(f"Request: {request}")
    if data_file:
        print(f"Data file: {data_file}")
    
    try:
        coordinator = MockCoordinatorAgent()
        result = coordinator.execute_workflow(request, data_file)
        
        if result['status'] == 'completed':
            print(f"\n✅ Complete workflow executed successfully!")
            
            print(f"\n📊 Workflow Summary:")
            print(f"   ID: {result['workflow_id']}")
            print(f"   Status: {result['status']}")
            print(f"   Agents Used: {', '.join(result['agents_used'])}")
            
            # Show results summary
            results = result.get('results', {})
            for step_name, step_result in results.items():
                status = step_result.get('status', 'unknown')
                print(f"   {step_name.replace('_', ' ').title()}: {status}")
            
            return True
        else:
            print(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
            return False
        
    except Exception as e:
        print(f"❌ Error in workflow: {e}")
        return False


def run_all_tests():
    """Run all agent tests"""
    print("🚀 Running all agent tests...\n")
    
    tests = [
        ("Data Analysis", lambda: test_data_analysis("sample_data.csv")),
        ("Research", lambda: test_research("AI market trends")),
        ("Report Generation", lambda: test_report_generation("Test Report")),
        ("Complete Workflow", lambda: test_full_workflow(
            "Analyze sales data and create market research report", 
            "sample_data.csv"
        ))
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"🧪 Testing: {test_name}")
        print('='*60)
        
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"❌ Test failed with exception: {e}")
            results.append((test_name, False))
    
    print(f"\n{'='*60}")
    print("📊 TEST RESULTS SUMMARY")
    print('='*60)
    
    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{test_name}: {status}")
    
    total_passed = sum(1 for _, success in results if success)
    print(f"\n🎯 Total: {total_passed}/{len(results)} tests passed")
    
    if total_passed == len(results):
        print("🎉 All tests passed! System is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")


def show_system_status():
    """Show system status"""
    print("📊 Strands Multi-Agent System Status")
    print("=" * 40)
    
    try:
        coordinator = MockCoordinatorAgent()
        status = coordinator.get_agent_status()
        
        print("\n🤖 Agent Status:")
        for agent_name, agent_info in status.items():
            status_emoji = "🟢" if agent_info['status'] in ['active', 'ready'] else "🔴"
            print(f"   {status_emoji} {agent_name.replace('_', ' ').title()}: {agent_info['status']}")
            print(f"      History: {agent_info['history_count']} actions")
        
        print("\n📁 Available Files:")
        current_dir = Path(".")
        csv_files = list(current_dir.glob("*.csv"))
        if csv_files:
            for file in csv_files:
                size = file.stat().st_size
                print(f"   📄 {file.name} ({size} bytes)")
        else:
            print("   No CSV files found in current directory")
        
        print(f"\n⏰ System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("✅ System Status: Online and Ready")
        
    except Exception as e:
        print(f"❌ Error checking system status: {e}")


def main():
    """Main CLI function"""
    parser = argparse.ArgumentParser(
        description="Demo CLI for Strands Multi-Agent System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_cli.py analyze sample_data.csv
  python demo_cli.py research "electric vehicle market"
  python demo_cli.py workflow "analyze sales and create report" sample_data.csv
  python demo_cli.py test-all
  python demo_cli.py status
        """
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
    
    # Workflow command
    workflow_parser = subparsers.add_parser('workflow', help='Test complete workflow')
    workflow_parser.add_argument('request', help='Workflow request')
    workflow_parser.add_argument('data_file', nargs='?', help='Optional data file')
    
    # Test all command
    subparsers.add_parser('test-all', help='Run all tests')
    
    # Status command
    subparsers.add_parser('status', help='Show system status')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    print(f"🤖 Strands Multi-Agent System Demo CLI")
    print(f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    if args.command == 'analyze':
        success = test_data_analysis(args.file_path)
        sys.exit(0 if success else 1)
    
    elif args.command == 'research':
        success = test_research(args.query)
        sys.exit(0 if success else 1)
    
    elif args.command == 'report':
        success = test_report_generation(args.title)
        sys.exit(0 if success else 1)
    
    elif args.command == 'workflow':
        success = test_full_workflow(args.request, args.data_file)
        sys.exit(0 if success else 1)
    
    elif args.command == 'test-all':
        run_all_tests()
    
    elif args.command == 'status':
        show_system_status()


if __name__ == "__main__":
    main()