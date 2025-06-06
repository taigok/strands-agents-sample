import streamlit as st
import pandas as pd
import os
import json
from datetime import datetime
from pathlib import Path
import tempfile
from typing import Dict, Any, List, Optional
import plotly.express as px
import plotly.graph_objects as go

from src.agents import (
    CoordinatorAgent,
    DataAnalystAgent,
    ResearchAgent,
    ReportGeneratorAgent
)
from src.config.settings import settings
import structlog

# Configure logging
logger = structlog.get_logger()

# Page configuration
st.set_page_config(
    page_title="Strands Multi-Agent System",
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
.agent-status {
    padding: 10px;
    border-radius: 5px;
    margin: 5px 0;
}
.agent-active {
    background-color: #d4edda;
    border: 1px solid #c3e6cb;
}
.agent-idle {
    background-color: #f8f9fa;
    border: 1px solid #dee2e6;
}
.metric-card {
    background-color: #ffffff;
    padding: 20px;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin: 10px 0;
}
</style>
""", unsafe_allow_html=True)


class MultiAgentApp:
    """Streamlit application for the Multi-Agent System"""
    
    def __init__(self):
        self.init_session_state()
        self.coordinator = CoordinatorAgent()
        
    def init_session_state(self):
        """Initialize session state variables"""
        if 'workflow_history' not in st.session_state:
            st.session_state.workflow_history = []
        if 'current_workflow' not in st.session_state:
            st.session_state.current_workflow = None
        if 'uploaded_files' not in st.session_state:
            st.session_state.uploaded_files = []
        if 'agent_logs' not in st.session_state:
            st.session_state.agent_logs = []
        if 'results' not in st.session_state:
            st.session_state.results = {}
    
    def run(self):
        """Main application entry point"""
        st.title("🤖 Strands Multi-Agent System")
        st.markdown("**Intelligent automation with specialized AI agents working together**")
        
        # Sidebar
        with st.sidebar:
            self.render_sidebar()
        
        # Main content
        tab1, tab2, tab3, tab4 = st.tabs([
            "🚀 New Task", 
            "📊 Agent Dashboard", 
            "📄 Results & Reports",
            "📜 Workflow History"
        ])
        
        with tab1:
            self.render_new_task_tab()
        
        with tab2:
            self.render_dashboard_tab()
        
        with tab3:
            self.render_results_tab()
        
        with tab4:
            self.render_history_tab()
    
    def render_sidebar(self):
        """Render sidebar with system information"""
        st.header("🎛️ System Control")
        
        # System status
        st.subheader("System Status")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Active Agents", "4", "✅")
        with col2:
            st.metric("Tasks Today", len(st.session_state.workflow_history), 
                     f"+{len(st.session_state.workflow_history)}")
        
        # Agent status
        st.subheader("Agent Status")
        agents = [
            ("🔍 Data Analyst", "Ready"),
            ("🌐 Research Agent", "Ready"),
            ("📝 Report Generator", "Ready"),
            ("🎯 Coordinator", "Active")
        ]
        
        for agent_name, status in agents:
            status_class = "agent-active" if status == "Active" else "agent-idle"
            st.markdown(
                f'<div class="agent-status {status_class}">{agent_name}: {status}</div>',
                unsafe_allow_html=True
            )
        
        # Settings
        st.subheader("⚙️ Settings")
        
        with st.expander("Model Configuration"):
            model_id = st.selectbox(
                "Bedrock Model",
                ["anthropic.claude-3-5-sonnet-20241022-v2:0"],
                index=0
            )
            
        with st.expander("Advanced Settings"):
            max_iterations = st.slider(
                "Max Agent Iterations",
                min_value=1,
                max_value=20,
                value=settings.agent_max_iterations
            )
            
            timeout = st.slider(
                "Task Timeout (seconds)",
                min_value=30,
                max_value=600,
                value=settings.agent_timeout_seconds
            )
    
    def render_new_task_tab(self):
        """Render the new task creation tab"""
        st.header("Create New Task")
        
        # Task type selection
        task_type = st.selectbox(
            "Select Task Type",
            [
                "📊 Data Analysis & Report",
                "🔍 Market Research & Analysis",
                "📈 Competitive Intelligence",
                "📝 Custom Multi-Agent Task"
            ]
        )
        
        # Task configuration based on type
        if task_type == "📊 Data Analysis & Report":
            self.render_data_analysis_task()
        elif task_type == "🔍 Market Research & Analysis":
            self.render_market_research_task()
        elif task_type == "📈 Competitive Intelligence":
            self.render_competitive_intel_task()
        else:
            self.render_custom_task()
    
    def render_data_analysis_task(self):
        """Render data analysis task configuration"""
        st.subheader("Data Analysis & Report Configuration")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Data Files",
            type=['csv', 'xlsx', 'xls'],
            accept_multiple_files=True,
            help="Upload CSV or Excel files for analysis"
        )
        
        if uploaded_files:
            st.session_state.uploaded_files = uploaded_files
            
            # Display uploaded files
            st.write("**Uploaded Files:**")
            for file in uploaded_files:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    st.text(file.name)
                with col2:
                    st.text(f"{file.size / 1024:.1f} KB")
                with col3:
                    if st.button("Preview", key=f"preview_{file.name}"):
                        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
                        st.dataframe(df.head(10))
        
        # Analysis configuration
        col1, col2 = st.columns(2)
        
        with col1:
            analysis_types = st.multiselect(
                "Analysis Types",
                [
                    "Statistical Summary",
                    "Trend Analysis",
                    "Correlation Analysis",
                    "Outlier Detection",
                    "Segmentation Analysis",
                    "Predictive Insights"
                ],
                default=["Statistical Summary", "Trend Analysis"]
            )
        
        with col2:
            report_sections = st.multiselect(
                "Report Sections",
                [
                    "Executive Summary",
                    "Data Overview",
                    "Key Findings",
                    "Detailed Analysis",
                    "Visualizations",
                    "Recommendations",
                    "Technical Appendix"
                ],
                default=["Executive Summary", "Key Findings", "Recommendations"]
            )
        
        # Additional research
        include_research = st.checkbox("Include Market Research", value=True)
        if include_research:
            research_queries = st.text_area(
                "Research Queries (one per line)",
                placeholder="Industry trends for this data\nCompetitor benchmarks\nMarket outlook",
                height=100
            )
        
        # Output configuration
        st.subheader("Output Configuration")
        col1, col2 = st.columns(2)
        
        with col1:
            output_format = st.selectbox(
                "Report Format",
                ["PDF", "Word Document", "HTML Dashboard", "All Formats"]
            )
        
        with col2:
            report_title = st.text_input(
                "Report Title",
                value=f"Analysis Report - {datetime.now().strftime('%B %Y')}"
            )
        
        # Execute button
        if st.button("🚀 Start Analysis", type="primary", use_container_width=True):
            if not uploaded_files:
                st.error("Please upload at least one data file")
            else:
                self.execute_data_analysis_task(
                    uploaded_files,
                    analysis_types,
                    report_sections,
                    research_queries.split('\n') if include_research else [],
                    output_format,
                    report_title
                )
    
    def render_market_research_task(self):
        """Render market research task configuration"""
        st.subheader("Market Research Configuration")
        
        # Research topic
        research_topic = st.text_input(
            "Research Topic",
            placeholder="e.g., Electric Vehicle Market in North America"
        )
        
        # Research aspects
        col1, col2 = st.columns(2)
        
        with col1:
            research_aspects = st.multiselect(
                "Research Aspects",
                [
                    "Market Size & Growth",
                    "Key Players & Competition",
                    "Customer Demographics",
                    "Technology Trends",
                    "Regulatory Environment",
                    "Investment & Funding",
                    "Future Outlook",
                    "SWOT Analysis"
                ],
                default=["Market Size & Growth", "Key Players & Competition", "Future Outlook"]
            )
        
        with col2:
            data_sources = st.multiselect(
                "Data Sources",
                [
                    "Industry Reports",
                    "News Articles",
                    "Academic Papers",
                    "Company Websites",
                    "Government Data",
                    "Social Media",
                    "Patents"
                ],
                default=["Industry Reports", "News Articles", "Company Websites"]
            )
        
        # Time horizon
        time_horizon = st.select_slider(
            "Analysis Time Horizon",
            options=["Current", "1 Year", "3 Years", "5 Years", "10 Years"],
            value="5 Years"
        )
        
        # Geographic focus
        geographic_focus = st.multiselect(
            "Geographic Focus",
            ["Global", "North America", "Europe", "Asia-Pacific", "Latin America", "Africa"],
            default=["North America"]
        )
        
        # Execute button
        if st.button("🔍 Start Research", type="primary", use_container_width=True):
            if not research_topic:
                st.error("Please enter a research topic")
            else:
                self.execute_market_research_task(
                    research_topic,
                    research_aspects,
                    data_sources,
                    time_horizon,
                    geographic_focus
                )
    
    def render_competitive_intel_task(self):
        """Render competitive intelligence task configuration"""
        st.subheader("Competitive Intelligence Configuration")
        
        # Company information
        col1, col2 = st.columns(2)
        
        with col1:
            target_company = st.text_input(
                "Your Company/Product",
                placeholder="e.g., Tesla Model 3"
            )
        
        with col2:
            competitors = st.text_area(
                "Competitors (one per line)",
                placeholder="BMW i4\nMercedes EQE\nAudi e-tron GT",
                height=100
            )
        
        # Analysis criteria
        analysis_criteria = st.multiselect(
            "Analysis Criteria",
            [
                "Product Features",
                "Pricing Strategy",
                "Market Share",
                "Customer Reviews",
                "Technology Stack",
                "Marketing Approach",
                "Distribution Channels",
                "Financial Performance",
                "Innovation Pipeline",
                "Brand Perception"
            ],
            default=["Product Features", "Pricing Strategy", "Market Share", "Customer Reviews"]
        )
        
        # Data file upload (optional)
        st.write("**Optional: Upload Internal Data**")
        internal_data = st.file_uploader(
            "Upload your company data for comparison",
            type=['csv', 'xlsx'],
            help="Upload internal metrics for deeper comparison"
        )
        
        # Execute button
        if st.button("📈 Start Analysis", type="primary", use_container_width=True):
            if not target_company or not competitors:
                st.error("Please enter your company and at least one competitor")
            else:
                self.execute_competitive_intel_task(
                    target_company,
                    competitors.split('\n'),
                    analysis_criteria,
                    internal_data
                )
    
    def render_custom_task(self):
        """Render custom multi-agent task configuration"""
        st.subheader("Custom Multi-Agent Task")
        
        # Task description
        task_description = st.text_area(
            "Describe Your Task",
            placeholder="Describe what you want the multi-agent system to accomplish...",
            height=150
        )
        
        # Agent selection
        st.write("**Select Agents to Use:**")
        col1, col2 = st.columns(2)
        
        with col1:
            use_data_analyst = st.checkbox("🔍 Data Analyst Agent", value=True)
            use_research = st.checkbox("🌐 Research Agent", value=True)
        
        with col2:
            use_report_gen = st.checkbox("📝 Report Generator", value=True)
            use_coordinator = st.checkbox("🎯 Coordinator (Recommended)", value=True, disabled=True)
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload Related Files (Optional)",
            type=['csv', 'xlsx', 'xls', 'pdf', 'txt'],
            accept_multiple_files=True
        )
        
        # Output preferences
        st.write("**Output Preferences:**")
        col1, col2 = st.columns(2)
        
        with col1:
            output_format = st.selectbox(
                "Preferred Output Format",
                ["Detailed Report", "Executive Summary", "Raw Analysis", "All Outputs"]
            )
        
        with col2:
            urgency = st.select_slider(
                "Task Priority",
                options=["Low", "Medium", "High", "Critical"],
                value="Medium"
            )
        
        # Execute button
        if st.button("🎯 Execute Task", type="primary", use_container_width=True):
            if not task_description:
                st.error("Please describe your task")
            else:
                self.execute_custom_task(
                    task_description,
                    {
                        "data_analyst": use_data_analyst,
                        "research": use_research,
                        "report_generator": use_report_gen
                    },
                    uploaded_files,
                    output_format,
                    urgency
                )
    
    def render_dashboard_tab(self):
        """Render the agent dashboard tab"""
        st.header("📊 Agent Performance Dashboard")
        
        # Metrics row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Tasks Completed",
                len(st.session_state.workflow_history),
                "+10%"
            )
        
        with col2:
            st.metric(
                "Average Task Time",
                "3.5 min",
                "-15%"
            )
        
        with col3:
            st.metric(
                "Success Rate",
                "98.5%",
                "+2.5%"
            )
        
        with col4:
            st.metric(
                "Active Workflows",
                "1" if st.session_state.current_workflow else "0"
            )
        
        # Agent activity chart
        st.subheader("Agent Activity Over Time")
        
        # Mock data for visualization
        activity_data = pd.DataFrame({
            'Time': pd.date_range(start='2024-01-01', periods=24, freq='H'),
            'Data Analyst': [5, 3, 7, 9, 12, 15, 18, 20, 22, 25, 23, 20, 18, 15, 12, 10, 8, 6, 4, 3, 2, 1, 0, 2],
            'Research Agent': [3, 5, 8, 10, 11, 13, 15, 17, 19, 20, 18, 16, 14, 12, 10, 8, 6, 4, 3, 2, 1, 0, 1, 2],
            'Report Generator': [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 19, 17, 15, 13, 11, 9, 7, 5, 3, 2, 1, 0, 0, 1]
        })
        
        fig = go.Figure()
        for agent in ['Data Analyst', 'Research Agent', 'Report Generator']:
            fig.add_trace(go.Scatter(
                x=activity_data['Time'],
                y=activity_data[agent],
                mode='lines',
                name=agent,
                line=dict(width=2)
            ))
        
        fig.update_layout(
            title="Agent Task Load (24 Hour View)",
            xaxis_title="Time",
            yaxis_title="Active Tasks",
            hovermode='x unified',
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Task distribution
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Task Distribution by Type")
            task_types = pd.DataFrame({
                'Type': ['Data Analysis', 'Research', 'Report Generation', 'Multi-Agent'],
                'Count': [45, 38, 42, 25]
            })
            
            fig = px.pie(task_types, values='Count', names='Type', hole=0.4)
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("Agent Utilization")
            utilization = pd.DataFrame({
                'Agent': ['Data Analyst', 'Research', 'Report Generator', 'Coordinator'],
                'Utilization': [78, 65, 82, 90]
            })
            
            fig = px.bar(utilization, x='Utilization', y='Agent', orientation='h',
                        color='Utilization', color_continuous_scale='Viridis')
            fig.update_layout(showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Recent agent logs
        st.subheader("Recent Agent Activity")
        
        if st.session_state.agent_logs:
            for log in st.session_state.agent_logs[-5:]:
                with st.expander(f"{log['timestamp']} - {log['agent']} - {log['action']}"):
                    st.write(log['details'])
        else:
            st.info("No recent agent activity to display")
    
    def render_results_tab(self):
        """Render the results and reports tab"""
        st.header("📄 Results & Reports")
        
        if st.session_state.results:
            # Filter options
            col1, col2, col3 = st.columns(3)
            
            with col1:
                filter_type = st.selectbox(
                    "Filter by Type",
                    ["All", "Reports", "Analysis", "Research"]
                )
            
            with col2:
                sort_by = st.selectbox(
                    "Sort by",
                    ["Date (Newest)", "Date (Oldest)", "Name", "Size"]
                )
            
            with col3:
                search = st.text_input("Search results", placeholder="Enter keywords...")
            
            # Results grid
            st.subheader("Available Results")
            
            for result_id, result in st.session_state.results.items():
                with st.container():
                    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                    
                    with col1:
                        st.write(f"**{result['title']}**")
                        st.caption(f"Created: {result['timestamp']}")
                    
                    with col2:
                        st.write(f"Type: {result['type']}")
                    
                    with col3:
                        st.write(f"Format: {result['format']}")
                    
                    with col4:
                        if st.button("View", key=f"view_{result_id}"):
                            self.view_result(result_id)
                        
                        if st.button("Download", key=f"download_{result_id}"):
                            self.download_result(result_id)
                    
                    st.divider()
        else:
            st.info("No results available yet. Complete a task to see results here.")
    
    def render_history_tab(self):
        """Render the workflow history tab"""
        st.header("📜 Workflow History")
        
        if st.session_state.workflow_history:
            # History timeline
            for i, workflow in enumerate(reversed(st.session_state.workflow_history)):
                with st.expander(
                    f"{workflow['timestamp']} - {workflow['title']}",
                    expanded=(i == 0)
                ):
                    col1, col2 = st.columns([2, 1])
                    
                    with col1:
                        st.write("**Description:**", workflow['description'])
                        st.write("**Status:**", workflow['status'])
                        st.write("**Duration:**", workflow.get('duration', 'N/A'))
                    
                    with col2:
                        st.write("**Agents Used:**")
                        for agent in workflow.get('agents_used', []):
                            st.write(f"- {agent}")
                    
                    if workflow.get('results'):
                        st.write("**Results Summary:**")
                        st.write(workflow['results'])
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button("Re-run", key=f"rerun_{i}"):
                            self.rerun_workflow(workflow)
                    with col2:
                        if st.button("View Details", key=f"details_{i}"):
                            self.view_workflow_details(workflow)
                    with col3:
                        if st.button("Export", key=f"export_{i}"):
                            self.export_workflow(workflow)
        else:
            st.info("No workflow history available yet.")
    
    def execute_data_analysis_task(self, files, analysis_types, report_sections, 
                                  research_queries, output_format, title):
        """Execute a data analysis task"""
        with st.spinner("🔄 Processing your request with multiple agents..."):
            # Save uploaded files temporarily
            file_paths = []
            for file in files:
                temp_path = Path(tempfile.gettempdir()) / file.name
                with open(temp_path, 'wb') as f:
                    f.write(file.getvalue())
                file_paths.append(str(temp_path))
            
            # Create task context
            context = {
                "files": file_paths,
                "analysis_types": analysis_types,
                "report_sections": report_sections,
                "research_queries": research_queries,
                "output_format": output_format,
                "title": title
            }
            
            # Execute with coordinator
            try:
                result = self.coordinator.generate_multi_source_report(
                    topic=title,
                    data_sources=file_paths,
                    research_queries=research_queries,
                    report_sections=report_sections,
                    output_path=f"/tmp/{title.replace(' ', '_')}.pdf"
                )
                
                # Store results
                result_id = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.results[result_id] = {
                    "title": title,
                    "type": "Data Analysis Report",
                    "format": output_format,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "result": result
                }
                
                # Add to history
                st.session_state.workflow_history.append({
                    "title": title,
                    "description": "Data analysis with report generation",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "status": "Completed",
                    "agents_used": ["Data Analyst", "Research Agent", "Report Generator"],
                    "results": f"Generated {output_format} report with {len(analysis_types)} analyses"
                })
                
                st.success("✅ Task completed successfully!")
                st.balloons()
                
                # Show preview
                with st.expander("View Results Preview"):
                    st.json(result)
                
            except Exception as e:
                st.error(f"❌ Error executing task: {str(e)}")
                logger.error("Task execution failed", error=str(e))
    
    def execute_market_research_task(self, topic, aspects, sources, time_horizon, geographic_focus):
        """Execute a market research task"""
        with st.spinner("🔍 Conducting comprehensive market research..."):
            try:
                result = self.coordinator.process_complex_request(
                    request=f"Conduct market research on {topic} for {', '.join(geographic_focus)} markets",
                    data_files=None,
                    output_format="pdf",
                    additional_requirements=[
                        f"Focus on: {', '.join(aspects)}",
                        f"Time horizon: {time_horizon}",
                        f"Use sources: {', '.join(sources)}"
                    ]
                )
                
                # Store results
                result_id = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.results[result_id] = {
                    "title": f"Market Research: {topic}",
                    "type": "Market Research",
                    "format": "PDF",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "result": result
                }
                
                st.success("✅ Market research completed!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    def execute_competitive_intel_task(self, company, competitors, criteria, internal_data):
        """Execute a competitive intelligence task"""
        with st.spinner("📈 Analyzing competitive landscape..."):
            try:
                # Handle internal data if provided
                data_path = None
                if internal_data:
                    temp_path = Path(tempfile.gettempdir()) / internal_data.name
                    with open(temp_path, 'wb') as f:
                        f.write(internal_data.getvalue())
                    data_path = str(temp_path)
                
                # Create research agent for competitive analysis
                research_agent = ResearchAgent()
                result = research_agent.analyze_competitors(
                    company=company,
                    competitors=competitors,
                    analysis_criteria=criteria
                )
                
                # Store results
                result_id = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.results[result_id] = {
                    "title": f"Competitive Analysis: {company}",
                    "type": "Competitive Intelligence",
                    "format": "Report",
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "result": result
                }
                
                st.success("✅ Competitive analysis completed!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    def execute_custom_task(self, description, agents, files, output_format, urgency):
        """Execute a custom multi-agent task"""
        with st.spinner("🎯 Executing custom multi-agent workflow..."):
            try:
                # Handle file uploads
                file_paths = []
                if files:
                    for file in files:
                        temp_path = Path(tempfile.gettempdir()) / file.name
                        with open(temp_path, 'wb') as f:
                            f.write(file.getvalue())
                        file_paths.append(str(temp_path))
                
                # Execute with coordinator
                result = self.coordinator.process_complex_request(
                    request=description,
                    data_files=file_paths if file_paths else None,
                    output_format=output_format.lower().replace(" ", "_"),
                    additional_requirements=[f"Priority: {urgency}"]
                )
                
                # Store results
                result_id = f"result_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                st.session_state.results[result_id] = {
                    "title": "Custom Task Result",
                    "type": "Custom Analysis",
                    "format": output_format,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "result": result
                }
                
                st.success("✅ Custom task completed!")
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    def view_result(self, result_id):
        """View a specific result"""
        result = st.session_state.results.get(result_id)
        if result:
            st.write(f"### {result['title']}")
            st.write(f"**Type:** {result['type']}")
            st.write(f"**Created:** {result['timestamp']}")
            st.json(result['result'])
    
    def download_result(self, result_id):
        """Download a specific result"""
        result = st.session_state.results.get(result_id)
        if result:
            # Convert result to downloadable format
            json_str = json.dumps(result, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_str,
                file_name=f"{result['title'].replace(' ', '_')}.json",
                mime="application/json"
            )
    
    def rerun_workflow(self, workflow):
        """Re-run a previous workflow"""
        st.info(f"Re-running workflow: {workflow['title']}")
        # Implementation would re-execute the workflow
    
    def view_workflow_details(self, workflow):
        """View detailed workflow information"""
        st.json(workflow)
    
    def export_workflow(self, workflow):
        """Export workflow configuration"""
        json_str = json.dumps(workflow, indent=2)
        st.download_button(
            label="Export Workflow",
            data=json_str,
            file_name=f"workflow_{workflow['timestamp'].replace(' ', '_')}.json",
            mime="application/json"
        )


def main():
    """Main application entry point"""
    app = MultiAgentApp()
    app.run()


if __name__ == "__main__":
    main()