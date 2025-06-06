from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from pathlib import Path
import json

from strands_agents import Agent
from strands_agents.tools import ToolDefinition
from strands_agents.models.bedrock import BedrockModel
from strands_agents.memory import ConversationBufferMemory

from ..tools.document_tools import (
    create_pdf_report,
    create_word_document,
    create_html_report,
    merge_documents,
    extract_text_from_pdf,
    create_template_document
)
from ..config.settings import settings
import structlog

logger = structlog.get_logger()


class ReportGeneratorAgent(Agent):
    """
    Report Generator Agent specialized in creating structured reports
    and presentations from analyzed data and research findings.
    """
    
    def __init__(self, agent_id: str = "report_generator"):
        # Initialize the Bedrock model
        bedrock_config = settings.get_bedrock_config()
        model = BedrockModel(**bedrock_config)
        
        # Initialize memory
        memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        
        # Define the agent's tools
        tools = [
            ToolDefinition(tool=create_pdf_report),
            ToolDefinition(tool=create_word_document),
            ToolDefinition(tool=create_html_report),
            ToolDefinition(tool=merge_documents),
            ToolDefinition(tool=extract_text_from_pdf),
            ToolDefinition(tool=create_template_document),
        ]
        
        # Define the agent's system prompt
        system_prompt = """You are a Report Generator Agent specialized in creating professional reports and documents.
        
Your responsibilities include:
1. Creating well-structured reports in multiple formats (PDF, Word, HTML)
2. Organizing content from various sources into coherent documents
3. Ensuring professional formatting and presentation
4. Creating executive summaries and key findings sections
5. Generating data visualizations descriptions and insights
6. Maintaining consistent style and branding

When creating reports:
- Start with a clear executive summary
- Organize content logically with clear sections
- Use professional language and tone
- Include data tables and visualization descriptions
- Highlight key findings and recommendations
- Ensure citations and sources are properly formatted
- Create actionable conclusions

Focus on clarity, professionalism, and delivering value to the reader."""
        
        # Initialize the parent Agent class
        super().__init__(
            agent_id=agent_id,
            model=model,
            tools=tools,
            memory=memory,
            system_prompt=system_prompt,
            max_iterations=settings.agent_max_iterations,
            verbose=True
        )
        
        logger.info("Report Generator Agent initialized", agent_id=agent_id)
    
    def create_comprehensive_report(
        self,
        title: str,
        data_insights: Dict[str, Any],
        research_findings: Dict[str, Any],
        report_type: str = "pdf",
        output_path: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create a comprehensive report combining data insights and research.
        
        Args:
            title: Report title
            data_insights: Insights from data analysis
            research_findings: Findings from research
            report_type: Type of report (pdf, docx, html)
            output_path: Optional output path
            
        Returns:
            Report generation results
        """
        try:
            if not output_path:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_path = f"/tmp/report_{timestamp}.{report_type}"
            
            prompt = f"""Create a comprehensive {report_type} report with the title: "{title}"

You have the following data insights:
{json.dumps(data_insights, indent=2)}

And these research findings:
{json.dumps(research_findings, indent=2)}

Structure the report with these sections:
1. Executive Summary
   - Key findings overview
   - Main recommendations
   - Critical metrics

2. Introduction
   - Background and context
   - Objectives and scope
   - Methodology overview

3. Data Analysis
   - Key metrics and statistics
   - Trends and patterns
   - Data quality observations

4. Research Findings
   - Market insights
   - Competitive landscape
   - Industry trends

5. Key Insights & Recommendations
   - Actionable recommendations
   - Strategic implications
   - Risk considerations

6. Conclusion
   - Summary of findings
   - Next steps
   - Future considerations

Save the report to: {output_path}

Ensure the report is professional, well-formatted, and provides clear value to executives."""
            
            result = self.run(prompt)
            
            logger.info(
                "Comprehensive report created",
                title=title,
                report_type=report_type,
                output_path=output_path
            )
            
            return {
                "title": title,
                "report_type": report_type,
                "output_path": output_path,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Report creation failed", title=title, error=str(e))
            raise
    
    def create_executive_summary(
        self,
        full_content: Dict[str, Any],
        max_pages: int = 2,
        focus_areas: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Create an executive summary from detailed content.
        
        Args:
            full_content: Full report content to summarize
            max_pages: Maximum pages for summary
            focus_areas: Specific areas to emphasize
            
        Returns:
            Executive summary content
        """
        try:
            focus_str = ""
            if focus_areas:
                focus_str = f"\nFocus particularly on: {', '.join(focus_areas)}"
            
            prompt = f"""Create a concise executive summary from the following content:

{json.dumps(full_content, indent=2)}

The executive summary should:
- Be no longer than {max_pages} pages when printed
- Highlight the most critical findings
- Present key metrics and data points
- Provide clear, actionable recommendations
- Use bullet points for readability
- Include a "Bottom Line" section{focus_str}

Structure:
1. Overview (2-3 sentences)
2. Key Findings (5-7 bullet points)
3. Critical Metrics (3-5 data points)
4. Recommendations (3-5 action items)
5. Bottom Line (1-2 sentences)

Make it compelling and easy to read for busy executives."""
            
            result = self.run(prompt)
            
            logger.info(
                "Executive summary created",
                max_pages=max_pages,
                focus_areas=focus_areas
            )
            
            return {
                "type": "executive_summary",
                "max_pages": max_pages,
                "focus_areas": focus_areas,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Executive summary creation failed", error=str(e))
            raise
    
    def create_presentation_slides(
        self,
        title: str,
        content: Dict[str, Any],
        num_slides: int = 10,
        slide_format: str = "content"
    ) -> Dict[str, Any]:
        """
        Create presentation slide content.
        
        Args:
            title: Presentation title
            content: Content to convert to slides
            num_slides: Target number of slides
            slide_format: Format type (content only or with speaker notes)
            
        Returns:
            Slide content and structure
        """
        try:
            prompt = f"""Create presentation slide content for: "{title}"

Based on this content:
{json.dumps(content, indent=2)}

Create approximately {num_slides} slides with the following structure:
1. Title Slide
2. Agenda/Overview
3-{num_slides-2}. Content Slides
{num_slides-1}. Key Takeaways
{num_slides}. Next Steps/Questions

For each slide provide:
- Slide Title
- Main Points (3-5 bullet points)
- Key Data/Metrics (if applicable)
- Visual Suggestion (chart type, diagram, etc.)
{"- Speaker Notes" if slide_format == "with_notes" else ""}

Guidelines:
- Use concise, impactful language
- One main idea per slide
- Include relevant data visualizations
- Maintain logical flow
- End with clear call-to-action

Format the output so it can be easily converted to actual slides."""
            
            result = self.run(prompt)
            
            logger.info(
                "Presentation slides created",
                title=title,
                num_slides=num_slides
            )
            
            return {
                "title": title,
                "num_slides": num_slides,
                "slide_format": slide_format,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Slide creation failed", title=title, error=str(e))
            raise
    
    def create_dashboard_report(
        self,
        metrics: Dict[str, Any],
        period: str,
        comparison_period: Optional[str] = None,
        output_format: str = "html"
    ) -> Dict[str, Any]:
        """
        Create a dashboard-style report with KPIs and metrics.
        
        Args:
            metrics: Dictionary of metrics and KPIs
            period: Reporting period
            comparison_period: Optional comparison period
            output_format: Output format (html, pdf)
            
        Returns:
            Dashboard report content
        """
        try:
            comparison_str = f" compared to {comparison_period}" if comparison_period else ""
            
            prompt = f"""Create a dashboard-style {output_format} report for {period}{comparison_str}.

Metrics provided:
{json.dumps(metrics, indent=2)}

Create a visually organized dashboard report with:

1. KPI Summary Section
   - Top 5-7 most important metrics
   - Current values and trends
   - Visual indicators (up/down arrows, colors)

2. Performance Overview
   - Key performance areas
   - Achievement vs targets
   - Period-over-period changes

3. Detailed Metrics
   - Organized by category
   - Include sparkline/trend descriptions
   - Highlight significant changes

4. Insights & Alerts
   - Notable achievements
   - Areas of concern
   - Anomalies or outliers

5. Quick Actions
   - Recommended immediate actions
   - Areas requiring attention

Use formatting that suggests visual elements:
- [CHART: description] for charts
- [METRIC: value, trend] for KPIs
- [ALERT: message] for warnings
- Color coding: Green (good), Yellow (caution), Red (concern)

Make it scannable and action-oriented."""
            
            result = self.run(prompt)
            
            logger.info(
                "Dashboard report created",
                period=period,
                output_format=output_format
            )
            
            return {
                "type": "dashboard",
                "period": period,
                "comparison_period": comparison_period,
                "output_format": output_format,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Dashboard report creation failed", error=str(e))
            raise
    
    def generate_report_from_template(
        self,
        template_type: str,
        data: Dict[str, Any],
        customizations: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate a report using predefined templates.
        
        Args:
            template_type: Type of template to use
            data: Data to populate the template
            customizations: Optional customizations
            
        Returns:
            Generated report content
        """
        try:
            custom_str = ""
            if customizations:
                custom_str = f"\nApply these customizations: {json.dumps(customizations, indent=2)}"
            
            prompt = f"""Generate a {template_type} report using the following data:

{json.dumps(data, indent=2)}
{custom_str}

Available template types and their purposes:
- "executive_summary": High-level overview for executives
- "technical_report": Detailed technical analysis
- "market_analysis": Market research and competitive analysis
- "financial_report": Financial metrics and analysis
- "project_status": Project progress and milestones
- "incident_report": Issue analysis and resolution

Based on the template type, create appropriate content that:
1. Follows standard structure for that report type
2. Includes all relevant sections
3. Maintains appropriate tone and detail level
4. Highlights critical information
5. Provides clear conclusions and next steps

Ensure the report is complete and ready for distribution."""
            
            result = self.run(prompt)
            
            logger.info(
                "Template report generated",
                template_type=template_type
            )
            
            return {
                "template_type": template_type,
                "customizations": customizations,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Template report generation failed", template_type=template_type, error=str(e))
            raise
    
    def combine_multiple_reports(
        self,
        report_paths: List[str],
        output_title: str,
        combination_type: str = "sequential",
        output_format: str = "pdf"
    ) -> Dict[str, Any]:
        """
        Combine multiple reports into a single document.
        
        Args:
            report_paths: List of report file paths
            output_title: Title for combined report
            combination_type: How to combine (sequential, merged, summarized)
            output_format: Output format
            
        Returns:
            Combined report information
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = f"/tmp/combined_report_{timestamp}.{output_format}"
            
            prompt = f"""Combine multiple reports into a single {output_format} document titled: "{output_title}"

Report files to combine:
{json.dumps(report_paths, indent=2)}

Combination type: {combination_type}
- "sequential": Append reports one after another with transitions
- "merged": Intelligently merge similar sections
- "summarized": Create a summary report from all inputs

Please:
1. Extract content from each report
2. Organize according to combination type
3. Create smooth transitions between sections
4. Eliminate redundancy (for merged/summarized)
5. Maintain consistent formatting
6. Add a table of contents
7. Include source attributions

Save the combined report to: {output_path}

Ensure the final document is cohesive and professional."""
            
            result = self.run(prompt)
            
            logger.info(
                "Reports combined",
                num_reports=len(report_paths),
                combination_type=combination_type,
                output_path=output_path
            )
            
            return {
                "output_title": output_title,
                "report_paths": report_paths,
                "combination_type": combination_type,
                "output_format": output_format,
                "output_path": output_path,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Report combination failed", error=str(e))
            raise