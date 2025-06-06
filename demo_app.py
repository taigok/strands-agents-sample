import streamlit as st
import pandas as pd
import json
import tempfile
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

from demo_agents import MockCoordinatorAgent

# Page configuration
st.set_page_config(
    page_title="Strands Multi-Agent System Demo",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
.stAlert {
    background-color: #f0f2f6;
    border-radius: 5px;
    padding: 10px;
}
.agent-card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 10px 0;
}
.success-card {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
    border-radius: 5px;
    padding: 15px;
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


def main():
    """Main application"""
    st.title("🤖 Strands Multi-Agent System Demo")
    st.markdown("**Intelligent automation with specialized AI agents working together**")
    
    # Initialize session state
    if 'coordinator' not in st.session_state:
        st.session_state.coordinator = MockCoordinatorAgent()
    if 'workflow_history' not in st.session_state:
        st.session_state.workflow_history = []
    
    # Sidebar
    with st.sidebar:
        st.header("🎛️ System Control")
        
        # Agent status
        st.subheader("Agent Status")
        status = st.session_state.coordinator.get_agent_status()
        
        for agent_name, agent_info in status.items():
            status_emoji = "🟢" if agent_info['status'] in ['active', 'ready'] else "🔴"
            st.write(f"{status_emoji} **{agent_name.title()}**: {agent_info['status']}")
        
        st.divider()
        
        # Quick stats
        st.subheader("📊 Quick Stats")
        st.metric("Workflows Completed", len(st.session_state.workflow_history))
        st.metric("System Status", "Online", "✅")
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs(["🚀 New Task", "📊 Dashboard", "📜 History"])
    
    with tab1:
        st.header("Create New Multi-Agent Task")
        
        # Task configuration
        col1, col2 = st.columns([2, 1])
        
        with col1:
            task_description = st.text_area(
                "Describe your task:",
                placeholder="e.g., Analyze sales data and create a market research report...",
                height=100
            )
        
        with col2:
            st.write("**Available Agents:**")
            st.write("🔍 Data Analyst")
            st.write("🌐 Research Agent")
            st.write("📝 Report Generator")
            st.write("🎯 Coordinator")
        
        # File upload
        uploaded_file = st.file_uploader(
            "Upload data file (optional):",
            type=['csv', 'xlsx', 'xls'],
            help="Upload a CSV or Excel file for data analysis"
        )
        
        # Show sample data option
        col1, col2 = st.columns(2)
        with col1:
            use_sample_data = st.checkbox("Use sample data for demo", value=True)
        with col2:
            if st.button("View Sample Data"):
                sample_df = pd.read_csv('sample_data.csv')
                st.dataframe(sample_df.head(10))
        
        # Execute button
        if st.button("🚀 Execute Multi-Agent Workflow", type="primary", use_container_width=True):
            if not task_description:
                st.error("Please describe your task")
            else:
                execute_workflow(task_description, uploaded_file, use_sample_data)
    
    with tab2:
        st.header("📊 Agent Dashboard")
        
        # Performance metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Tasks", len(st.session_state.workflow_history), "+1")
        with col2:
            success_rate = 100 if st.session_state.workflow_history else 0
            st.metric("Success Rate", f"{success_rate}%", "100%")
        with col3:
            st.metric("Active Agents", "4", "🟢")
        with col4:
            avg_time = "2.5 min" if st.session_state.workflow_history else "N/A"
            st.metric("Avg. Task Time", avg_time)
        
        # Agent activity chart
        if st.session_state.workflow_history:
            st.subheader("Recent Workflow Activity")
            
            # Create mock activity data
            activity_data = []
            for i, workflow in enumerate(st.session_state.workflow_history[-10:]):
                for agent in workflow.get('agents_used', []):
                    activity_data.append({
                        'Workflow': f"Task {i+1}",
                        'Agent': agent.replace('_', ' ').title(),
                        'Duration': 2 + i * 0.5,  # Mock duration
                        'Status': workflow.get('status', 'completed')
                    })
            
            if activity_data:
                df = pd.DataFrame(activity_data)
                fig = px.bar(df, x='Workflow', y='Duration', color='Agent',
                           title="Agent Task Duration by Workflow")
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No workflow data available yet. Run a task to see analytics.")
    
    with tab3:
        st.header("📜 Workflow History")
        
        if st.session_state.workflow_history:
            for i, workflow in enumerate(reversed(st.session_state.workflow_history)):
                with st.expander(f"Workflow {len(st.session_state.workflow_history) - i}: {workflow.get('request', 'Unknown')[:60]}..."):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.write("**Status:**", workflow.get('status', 'Unknown'))
                        st.write("**Timestamp:**", workflow.get('timestamp', 'Unknown'))
                        st.write("**Request:**", workflow.get('request', 'N/A'))
                    
                    with col2:
                        st.write("**Agents Used:**")
                        for agent in workflow.get('agents_used', []):
                            st.write(f"- {agent.replace('_', ' ').title()}")
                    
                    # Show results summary
                    if workflow.get('results'):
                        st.write("**Results Summary:**")
                        results = workflow['results']
                        
                        if 'data_analysis' in results:
                            data_result = results['data_analysis']
                            if data_result.get('status') == 'completed':
                                analysis = data_result.get('analysis', {})
                                file_info = analysis.get('file_info', {})
                                st.write(f"- Data Analysis: {file_info.get('shape', 'N/A')} dataset analyzed")
                        
                        if 'market_research' in results:
                            research_result = results['market_research']
                            if research_result.get('status') == 'completed':
                                research = research_result.get('research', {})
                                st.write(f"- Market Research: {len(research.get('findings', {}))} aspects analyzed")
                        
                        if 'final_report' in results:
                            report_result = results['final_report']
                            if report_result.get('status') == 'completed':
                                report = report_result.get('report', {})
                                st.write(f"- Report Generated: {len(report.get('sections', {}))} sections")
        else:
            st.info("No workflow history available yet.")


def execute_workflow(task_description: str, uploaded_file, use_sample_data: bool):
    """Execute a multi-agent workflow"""
    
    # Show progress
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Determine data file
        data_file = None
        if uploaded_file:
            # Save uploaded file temporarily
            temp_path = Path(tempfile.gettempdir()) / uploaded_file.name
            with open(temp_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            data_file = str(temp_path)
        elif use_sample_data:
            data_file = "sample_data.csv"
        
        status_text.text("🎯 Initializing workflow...")
        progress_bar.progress(10)
        
        # Execute workflow
        status_text.text("🔄 Executing multi-agent workflow...")
        progress_bar.progress(30)
        
        result = st.session_state.coordinator.execute_workflow(
            request=task_description,
            data_file=data_file
        )
        
        progress_bar.progress(100)
        status_text.text("✅ Workflow completed!")
        
        # Store in history
        st.session_state.workflow_history.append(result)
        
        # Show results
        if result['status'] == 'completed':
            st.success("🎉 Multi-agent workflow completed successfully!")
            
            # Results summary
            st.markdown("### 📋 Workflow Results")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Workflow ID", result['workflow_id'][-8:])
            with col2:
                st.metric("Agents Used", len(result['agents_used']))
            with col3:
                st.metric("Status", result['status'].title(), "✅")
            
            # Detailed results
            results = result.get('results', {})
            
            # Data Analysis Results
            if 'data_analysis' in results:
                with st.expander("🔍 Data Analysis Results", expanded=True):
                    data_result = results['data_analysis']
                    if data_result.get('status') == 'completed':
                        analysis = data_result.get('analysis', {})
                        
                        # File info
                        file_info = analysis.get('file_info', {})
                        if file_info:
                            st.write(f"**Dataset:** {file_info.get('shape', 'N/A')} (rows × columns)")
                            st.write(f"**Columns:** {', '.join(file_info.get('columns', []))}")
                        
                        # Insights
                        insights = analysis.get('insights', [])
                        if insights:
                            st.write("**Key Insights:**")
                            for insight in insights[:5]:  # Show first 5
                                st.write(f"- {insight}")
                        
                        # Show data if available
                        if data_file and Path(data_file).exists():
                            try:
                                df = pd.read_csv(data_file)
                                st.write("**Data Preview:**")
                                st.dataframe(df.head(10))
                                
                                # Simple visualization
                                numeric_cols = df.select_dtypes(include=['number']).columns
                                if len(numeric_cols) >= 2:
                                    col1, col2 = numeric_cols[:2]
                                    fig = px.scatter(df, x=col1, y=col2, title=f"{col1} vs {col2}")
                                    st.plotly_chart(fig, use_container_width=True)
                            except Exception as e:
                                st.warning(f"Could not display data: {e}")
            
            # Market Research Results
            if 'market_research' in results:
                with st.expander("🌐 Market Research Results", expanded=True):
                    research_result = results['market_research']
                    if research_result.get('status') == 'completed':
                        research = research_result.get('research', {})
                        
                        st.write(f"**Topic:** {research.get('topic', 'N/A')}")
                        st.write(f"**Aspects Analyzed:** {len(research.get('findings', {}))}")
                        
                        # Show findings
                        findings = research.get('findings', {})
                        for aspect, finding in findings.items():
                            st.write(f"**{aspect}:**")
                            st.write(f"- {finding.get('summary', 'No summary available')}")
                        
                        # Overall insights
                        insights = research.get('overall_insights', [])
                        if insights:
                            st.write("**Overall Insights:**")
                            for insight in insights:
                                st.write(f"- {insight}")
            
            # Final Report
            if 'final_report' in results:
                with st.expander("📝 Generated Report", expanded=True):
                    report_result = results['final_report']
                    if report_result.get('status') == 'completed':
                        report = report_result.get('report', {})
                        
                        st.write(f"**Title:** {report.get('title', 'N/A')}")
                        st.write(f"**Generated:** {report.get('generated_at', 'N/A')}")
                        
                        # Show sections
                        sections = report.get('sections', {})
                        for section_key, section in sections.items():
                            st.subheader(section.get('title', section_key))
                            st.write(section.get('content', 'No content available'))
                            
                            if 'items' in section:
                                for item in section['items']:
                                    st.write(f"- {item}")
            
            # Download option
            st.markdown("### 💾 Download Results")
            result_json = json.dumps(result, indent=2, default=str)
            st.download_button(
                label="📥 Download Full Results (JSON)",
                data=result_json,
                file_name=f"workflow_results_{result['workflow_id']}.json",
                mime="application/json"
            )
        
        else:
            st.error(f"❌ Workflow failed: {result.get('error', 'Unknown error')}")
    
    except Exception as e:
        st.error(f"❌ Error executing workflow: {str(e)}")
        progress_bar.progress(0)
        status_text.text("❌ Workflow failed")


if __name__ == "__main__":
    main()