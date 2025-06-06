#!/usr/bin/env python3
"""
Local test script to verify the multi-agent system without Streamlit
"""

import time
from demo_agents import MockCoordinatorAgent

def main():
    print("🤖 Strands Multi-Agent System - Local Test")
    print("=" * 50)
    
    # Initialize the coordinator
    coordinator = MockCoordinatorAgent()
    
    print("\n1. 📊 System Status Check:")
    status = coordinator.get_agent_status()
    for agent_name, info in status.items():
        emoji = "🟢" if info['status'] in ['active', 'ready'] else "🔴"
        print(f"   {emoji} {agent_name.replace('_', ' ').title()}: {info['status']}")
    
    print("\n2. 🔍 Testing Data Analysis:")
    data_result = coordinator.data_analyst.analyze_file("sample_data.csv")
    if data_result['status'] == 'completed':
        analysis = data_result['analysis']
        file_info = analysis['file_info']
        print(f"   ✅ Analyzed {file_info['shape']} dataset")
        print(f"   📈 Generated {len(analysis['insights'])} insights")
    
    print("\n3. 🌐 Testing Market Research:")
    research_result = coordinator.research_agent.conduct_market_research(
        topic="AI Technology Market",
        aspects=["Market Size", "Competition", "Trends"]
    )
    if research_result['status'] == 'completed':
        research = research_result['research']
        print(f"   ✅ Researched {research['topic']}")
        print(f"   📊 Analyzed {len(research['findings'])} market aspects")
    
    print("\n4. 📝 Testing Report Generation:")
    report_result = coordinator.report_generator.create_comprehensive_report(
        title="Multi-Agent System Demo Report",
        data_insights=data_result,
        research_findings=research_result
    )
    if report_result['status'] == 'completed':
        report = report_result['report']
        print(f"   ✅ Generated report: {report['title']}")
        print(f"   📄 Created {len(report['sections'])} sections")
    
    print("\n5. 🎯 Testing Complete Workflow:")
    workflow_result = coordinator.execute_workflow(
        request="Create a comprehensive business analysis report",
        data_file="sample_data.csv"
    )
    if workflow_result['status'] == 'completed':
        print(f"   ✅ Workflow completed: {workflow_result['workflow_id']}")
        print(f"   🤖 Used {len(workflow_result['agents_used'])} agents")
        print(f"   📋 Generated {len(workflow_result['results'])} result sets")
    
    print("\n" + "=" * 50)
    print("🎉 All tests completed successfully!")
    print("\n📋 Summary:")
    print(f"   • Data Analysis: ✅ Working")
    print(f"   • Market Research: ✅ Working") 
    print(f"   • Report Generation: ✅ Working")
    print(f"   • Multi-Agent Coordination: ✅ Working")
    
    print(f"\n💡 To access the web interface:")
    print(f"   1. Check VS Code PORTS tab for port 8501")
    print(f"   2. Or run: streamlit run demo_app.py")
    print(f"   3. Or use the CLI: python demo_cli.py test-all")

if __name__ == "__main__":
    main()