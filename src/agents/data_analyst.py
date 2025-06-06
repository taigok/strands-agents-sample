from typing import Dict, Any, List, Optional, Union
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
import json

from strands_agents import Agent
from strands_agents.tools import ToolDefinition
from strands_agents.models.bedrock import BedrockModel
from strands_agents.memory import ConversationBufferMemory

from ..tools.data_tools import (
    load_csv_file,
    load_excel_file,
    analyze_dataframe,
    filter_dataframe,
    aggregate_dataframe,
    pivot_dataframe,
    export_dataframe,
    detect_outliers
)
from ..config.settings import settings
import structlog

logger = structlog.get_logger()


class DataAnalystAgent(Agent):
    """
    Data Analyst Agent specialized in processing and analyzing data files.
    Capable of loading various data formats, performing statistical analysis,
    and generating insights from datasets.
    """
    
    def __init__(self, agent_id: str = "data_analyst"):
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
            ToolDefinition(tool=load_csv_file),
            ToolDefinition(tool=load_excel_file),
            ToolDefinition(tool=analyze_dataframe),
            ToolDefinition(tool=filter_dataframe),
            ToolDefinition(tool=aggregate_dataframe),
            ToolDefinition(tool=pivot_dataframe),
            ToolDefinition(tool=export_dataframe),
            ToolDefinition(tool=detect_outliers),
        ]
        
        # Define the agent's system prompt
        system_prompt = """You are a Data Analyst Agent specialized in processing and analyzing data.
        
Your responsibilities include:
1. Loading and processing data files (CSV, Excel)
2. Performing comprehensive statistical analysis
3. Identifying patterns, trends, and anomalies in data
4. Creating aggregations and pivot tables
5. Providing actionable insights based on data analysis

When analyzing data:
- Start by loading the data and understanding its structure
- Check for data quality issues (missing values, outliers, inconsistencies)
- Perform appropriate statistical analysis based on the data type
- Look for correlations and patterns
- Provide clear, actionable insights
- Suggest visualizations that would be helpful

Always explain your findings in business-friendly language while maintaining technical accuracy."""
        
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
        
        logger.info("Data Analyst Agent initialized", agent_id=agent_id)
    
    def analyze_file(self, file_path: str, analysis_type: str = "comprehensive") -> Dict[str, Any]:
        """
        Analyze a data file and return insights.
        
        Args:
            file_path: Path to the data file
            analysis_type: Type of analysis to perform
            
        Returns:
            Dictionary containing analysis results
        """
        try:
            file_extension = Path(file_path).suffix.lower()
            
            # Construct the analysis prompt
            prompt = f"""Please analyze the data file at: {file_path}
            
Perform a {analysis_type} analysis including:
1. Load the file and examine its structure
2. Check data quality (missing values, data types)
3. Generate summary statistics
4. Identify key patterns and trends
5. Detect any anomalies or outliers
6. Provide actionable insights and recommendations

Return a structured analysis with clear findings."""
            
            # Run the agent
            result = self.run(prompt)
            
            logger.info(
                "File analysis completed",
                file_path=file_path,
                analysis_type=analysis_type
            )
            
            return {
                "file_path": file_path,
                "analysis_type": analysis_type,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("File analysis failed", file_path=file_path, error=str(e))
            raise
    
    def compare_datasets(
        self,
        file_path1: str,
        file_path2: str,
        comparison_columns: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Compare two datasets and identify differences.
        
        Args:
            file_path1: Path to first dataset
            file_path2: Path to second dataset
            comparison_columns: Specific columns to compare
            
        Returns:
            Comparison results
        """
        try:
            columns_str = f"columns: {', '.join(comparison_columns)}" if comparison_columns else "all columns"
            
            prompt = f"""Compare the following two datasets:
1. Dataset 1: {file_path1}
2. Dataset 2: {file_path2}

Focus on comparing {columns_str}.

Please:
1. Load both datasets
2. Compare their structures (columns, data types, row counts)
3. Identify common and unique columns
4. Compare statistical properties of numerical columns
5. Identify significant differences in the data
6. Provide insights on what changed between the datasets

Return a detailed comparison report."""
            
            result = self.run(prompt)
            
            logger.info(
                "Dataset comparison completed",
                file1=file_path1,
                file2=file_path2
            )
            
            return {
                "file_path1": file_path1,
                "file_path2": file_path2,
                "comparison_columns": comparison_columns,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Dataset comparison failed", error=str(e))
            raise
    
    def generate_report_data(
        self,
        file_path: str,
        report_sections: List[str]
    ) -> Dict[str, Any]:
        """
        Generate data and insights for a report.
        
        Args:
            file_path: Path to the data file
            report_sections: List of report sections to generate
            
        Returns:
            Report data organized by sections
        """
        try:
            sections_str = "\n".join([f"- {section}" for section in report_sections])
            
            prompt = f"""Analyze the data file at {file_path} and generate content for a report with the following sections:

{sections_str}

For each section:
1. Provide relevant data analysis
2. Include key statistics and metrics
3. Identify important findings
4. Suggest data tables or visualizations
5. Write clear, concise insights

Format the output so it can be easily used in a report."""
            
            result = self.run(prompt)
            
            logger.info(
                "Report data generated",
                file_path=file_path,
                sections=len(report_sections)
            )
            
            return {
                "file_path": file_path,
                "report_sections": report_sections,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Report data generation failed", error=str(e))
            raise
    
    def perform_segmentation(
        self,
        file_path: str,
        segmentation_columns: List[str],
        target_column: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform data segmentation analysis.
        
        Args:
            file_path: Path to the data file
            segmentation_columns: Columns to use for segmentation
            target_column: Optional target column to analyze by segment
            
        Returns:
            Segmentation analysis results
        """
        try:
            target_str = f"analyzing '{target_column}'" if target_column else "analyzing all relevant metrics"
            
            prompt = f"""Perform segmentation analysis on the data file at {file_path}.

Segment the data by: {', '.join(segmentation_columns)}
Focus on {target_str} across segments.

Please:
1. Load the data and create segments based on the specified columns
2. Calculate segment sizes and proportions
3. Analyze key metrics for each segment
4. Identify significant differences between segments
5. Rank segments by importance/performance
6. Provide actionable insights for each segment

Return a comprehensive segmentation analysis."""
            
            result = self.run(prompt)
            
            logger.info(
                "Segmentation analysis completed",
                file_path=file_path,
                segments=segmentation_columns
            )
            
            return {
                "file_path": file_path,
                "segmentation_columns": segmentation_columns,
                "target_column": target_column,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Segmentation analysis failed", error=str(e))
            raise
    
    def forecast_trends(
        self,
        file_path: str,
        time_column: str,
        value_columns: List[str],
        forecast_periods: int = 12
    ) -> Dict[str, Any]:
        """
        Analyze trends and provide forecasts.
        
        Args:
            file_path: Path to the data file
            time_column: Column containing time/date information
            value_columns: Columns to forecast
            forecast_periods: Number of periods to forecast
            
        Returns:
            Trend analysis and forecast results
        """
        try:
            prompt = f"""Analyze trends and provide forecasts for the data file at {file_path}.

Time column: {time_column}
Value columns to forecast: {', '.join(value_columns)}
Forecast periods: {forecast_periods}

Please:
1. Load the data and ensure it's sorted by time
2. Analyze historical trends for each value column
3. Identify seasonality, cycles, or patterns
4. Calculate growth rates and trend directions
5. Provide simple forecasts for the next {forecast_periods} periods
6. Identify potential risks or opportunities in the trends
7. Suggest factors that might impact future values

Note: Use simple trend analysis and extrapolation methods suitable for business planning."""
            
            result = self.run(prompt)
            
            logger.info(
                "Trend forecast completed",
                file_path=file_path,
                forecast_periods=forecast_periods
            )
            
            return {
                "file_path": file_path,
                "time_column": time_column,
                "value_columns": value_columns,
                "forecast_periods": forecast_periods,
                "timestamp": datetime.now().isoformat(),
                "result": result
            }
            
        except Exception as e:
            logger.error("Trend forecast failed", error=str(e))
            raise