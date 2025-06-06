import pytest
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from src.agents.data_analyst import DataAnalystAgent
from src.tools.data_tools import load_csv_file, analyze_dataframe


class TestDataAnalystAgent:
    """Test suite for the Data Analyst Agent"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.sample_data = pd.DataFrame({
            'date': pd.date_range('2024-01-01', periods=10),
            'sales': [100, 120, 150, 130, 180, 200, 175, 190, 220, 250],
            'region': ['North', 'South', 'North', 'South', 'North'] * 2,
            'category': ['A', 'B', 'A', 'B', 'A', 'B', 'A', 'B', 'A', 'B']
        })
    
    def test_load_csv_file_tool(self):
        """Test CSV file loading tool"""
        # Create temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            # Test loading
            df = load_csv_file(temp_path)
            
            assert isinstance(df, pd.DataFrame)
            assert len(df) == 10
            assert 'sales' in df.columns
            assert 'region' in df.columns
        finally:
            # Clean up
            Path(temp_path).unlink()
    
    def test_analyze_dataframe_tool(self):
        """Test dataframe analysis tool"""
        result = analyze_dataframe(self.sample_data)
        
        assert isinstance(result, dict)
        assert 'shape' in result
        assert 'columns' in result
        assert 'summary_stats' in result
        assert 'missing_values' in result
        
        # Check shape
        assert result['shape'] == (10, 4)
        
        # Check columns
        expected_columns = ['date', 'sales', 'region', 'category']
        assert result['columns'] == expected_columns
        
        # Check that sales statistics are present
        assert 'sales' in result['summary_stats']
    
    @patch('src.agents.data_analyst.BedrockModel')
    def test_data_analyst_agent_initialization(self, mock_bedrock_model):
        """Test Data Analyst Agent initialization"""
        mock_bedrock_model.return_value = Mock()
        
        agent = DataAnalystAgent()
        
        assert agent.agent_id == "data_analyst"
        assert len(agent.tools) > 0
        
        # Check that the agent has the expected tools
        tool_names = [tool.tool.__name__ for tool in agent.tools]
        expected_tools = [
            'load_csv_file',
            'load_excel_file', 
            'analyze_dataframe',
            'filter_dataframe',
            'aggregate_dataframe'
        ]
        
        for expected_tool in expected_tools:
            assert expected_tool in tool_names
    
    @patch('src.agents.data_analyst.BedrockModel')
    def test_analyze_file_method(self, mock_bedrock_model):
        """Test the analyze_file method"""
        # Mock the model and run method
        mock_model = Mock()
        mock_bedrock_model.return_value = mock_model
        
        agent = DataAnalystAgent()
        agent.run = Mock(return_value="Analysis complete with insights")
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            self.sample_data.to_csv(f.name, index=False)
            temp_path = f.name
        
        try:
            result = agent.analyze_file(temp_path, "comprehensive")
            
            assert isinstance(result, dict)
            assert 'file_path' in result
            assert 'analysis_type' in result
            assert 'result' in result
            assert result['file_path'] == temp_path
            assert result['analysis_type'] == "comprehensive"
            
            # Verify that the run method was called
            agent.run.assert_called_once()
        finally:
            Path(temp_path).unlink()
    
    def test_sample_data_integrity(self):
        """Test that our sample data is correctly structured"""
        assert len(self.sample_data) == 10
        assert self.sample_data['sales'].sum() == 1715
        assert len(self.sample_data['region'].unique()) == 2
        assert len(self.sample_data['category'].unique()) == 2
        
        # Check data types
        assert self.sample_data['sales'].dtype in ['int64', 'float64']
        assert self.sample_data['region'].dtype == 'object'