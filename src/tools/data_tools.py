import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
import json
from datetime import datetime
from strands_agents.tools import tool
import structlog

logger = structlog.get_logger()


@tool
def load_csv_file(file_path: str, encoding: str = "utf-8") -> pd.DataFrame:
    """
    Load a CSV file into a pandas DataFrame.
    
    Args:
        file_path: Path to the CSV file
        encoding: File encoding (default: utf-8)
        
    Returns:
        DataFrame containing the CSV data
    """
    try:
        df = pd.read_csv(file_path, encoding=encoding)
        logger.info("CSV file loaded", file_path=file_path, shape=df.shape)
        return df
    except Exception as e:
        logger.error("Failed to load CSV", file_path=file_path, error=str(e))
        raise


@tool
def load_excel_file(file_path: str, sheet_name: Optional[str] = None) -> pd.DataFrame:
    """
    Load an Excel file into a pandas DataFrame.
    
    Args:
        file_path: Path to the Excel file
        sheet_name: Name of the sheet to load (default: first sheet)
        
    Returns:
        DataFrame containing the Excel data
    """
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logger.info("Excel file loaded", file_path=file_path, shape=df.shape)
        return df
    except Exception as e:
        logger.error("Failed to load Excel", file_path=file_path, error=str(e))
        raise


@tool
def analyze_dataframe(df: pd.DataFrame) -> Dict[str, Any]:
    """
    Perform comprehensive statistical analysis on a DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        Dictionary containing analysis results
    """
    try:
        analysis = {
            "shape": df.shape,
            "columns": list(df.columns),
            "dtypes": df.dtypes.to_dict(),
            "missing_values": df.isnull().sum().to_dict(),
            "summary_stats": {},
            "correlations": {},
            "unique_counts": {}
        }
        
        # Summary statistics for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        if len(numeric_cols) > 0:
            analysis["summary_stats"] = df[numeric_cols].describe().to_dict()
            
            # Correlation matrix
            if len(numeric_cols) > 1:
                analysis["correlations"] = df[numeric_cols].corr().to_dict()
        
        # Unique value counts for categorical columns
        categorical_cols = df.select_dtypes(include=['object', 'category']).columns
        for col in categorical_cols[:10]:  # Limit to first 10 categorical columns
            analysis["unique_counts"][col] = df[col].value_counts().head(10).to_dict()
        
        logger.info("DataFrame analysis completed", shape=df.shape)
        return analysis
        
    except Exception as e:
        logger.error("Failed to analyze DataFrame", error=str(e))
        raise


@tool
def filter_dataframe(
    df: pd.DataFrame,
    column: str,
    operator: str,
    value: Union[str, int, float, List]
) -> pd.DataFrame:
    """
    Filter a DataFrame based on a condition.
    
    Args:
        df: Input DataFrame
        column: Column name to filter on
        operator: Comparison operator (==, !=, >, <, >=, <=, in, not_in, contains)
        value: Value to compare against
        
    Returns:
        Filtered DataFrame
    """
    try:
        if column not in df.columns:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        
        if operator == "==":
            mask = df[column] == value
        elif operator == "!=":
            mask = df[column] != value
        elif operator == ">":
            mask = df[column] > value
        elif operator == "<":
            mask = df[column] < value
        elif operator == ">=":
            mask = df[column] >= value
        elif operator == "<=":
            mask = df[column] <= value
        elif operator == "in":
            mask = df[column].isin(value)
        elif operator == "not_in":
            mask = ~df[column].isin(value)
        elif operator == "contains":
            mask = df[column].astype(str).str.contains(str(value), case=False)
        else:
            raise ValueError(f"Unknown operator: {operator}")
        
        filtered_df = df[mask]
        logger.info(
            "DataFrame filtered",
            column=column,
            operator=operator,
            original_shape=df.shape,
            filtered_shape=filtered_df.shape
        )
        
        return filtered_df
        
    except Exception as e:
        logger.error("Failed to filter DataFrame", error=str(e))
        raise


@tool
def aggregate_dataframe(
    df: pd.DataFrame,
    group_by: Union[str, List[str]],
    aggregations: Dict[str, Union[str, List[str]]]
) -> pd.DataFrame:
    """
    Perform aggregation operations on a DataFrame.
    
    Args:
        df: Input DataFrame
        group_by: Column(s) to group by
        aggregations: Dictionary mapping columns to aggregation functions
                     e.g., {"amount": ["sum", "mean"], "count": "sum"}
        
    Returns:
        Aggregated DataFrame
    """
    try:
        if isinstance(group_by, str):
            group_by = [group_by]
        
        # Validate columns exist
        for col in group_by:
            if col not in df.columns:
                raise ValueError(f"Group by column '{col}' not found")
        
        for col in aggregations.keys():
            if col not in df.columns:
                raise ValueError(f"Aggregation column '{col}' not found")
        
        # Perform aggregation
        result = df.groupby(group_by).agg(aggregations).reset_index()
        
        # Flatten column names if multiple aggregations
        if any(isinstance(agg, list) for agg in aggregations.values()):
            result.columns = ['_'.join(col).strip() if col[1] else col[0] 
                            for col in result.columns.values]
        
        logger.info(
            "DataFrame aggregated",
            group_by=group_by,
            result_shape=result.shape
        )
        
        return result
        
    except Exception as e:
        logger.error("Failed to aggregate DataFrame", error=str(e))
        raise


@tool
def pivot_dataframe(
    df: pd.DataFrame,
    index: Union[str, List[str]],
    columns: str,
    values: str,
    aggfunc: str = "sum"
) -> pd.DataFrame:
    """
    Create a pivot table from a DataFrame.
    
    Args:
        df: Input DataFrame
        index: Column(s) to use as index
        columns: Column to use for pivot columns
        values: Column to aggregate
        aggfunc: Aggregation function (sum, mean, count, etc.)
        
    Returns:
        Pivoted DataFrame
    """
    try:
        pivot_table = pd.pivot_table(
            df,
            index=index,
            columns=columns,
            values=values,
            aggfunc=aggfunc,
            fill_value=0
        ).reset_index()
        
        logger.info(
            "Pivot table created",
            index=index,
            columns=columns,
            values=values,
            shape=pivot_table.shape
        )
        
        return pivot_table
        
    except Exception as e:
        logger.error("Failed to create pivot table", error=str(e))
        raise


@tool
def export_dataframe(
    df: pd.DataFrame,
    file_path: str,
    format: str = "csv",
    **kwargs
) -> str:
    """
    Export a DataFrame to various formats.
    
    Args:
        df: DataFrame to export
        file_path: Output file path
        format: Export format (csv, excel, json, parquet)
        **kwargs: Additional format-specific parameters
        
    Returns:
        Path to the exported file
    """
    try:
        output_path = Path(file_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        if format == "csv":
            df.to_csv(output_path, index=False, **kwargs)
        elif format == "excel":
            df.to_excel(output_path, index=False, **kwargs)
        elif format == "json":
            df.to_json(output_path, orient=kwargs.get("orient", "records"))
        elif format == "parquet":
            df.to_parquet(output_path, index=False, **kwargs)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(
            "DataFrame exported",
            format=format,
            file_path=str(output_path),
            shape=df.shape
        )
        
        return str(output_path)
        
    except Exception as e:
        logger.error("Failed to export DataFrame", error=str(e))
        raise


@tool
def detect_outliers(
    df: pd.DataFrame,
    columns: Optional[List[str]] = None,
    method: str = "iqr",
    threshold: float = 1.5
) -> pd.DataFrame:
    """
    Detect outliers in numeric columns using various methods.
    
    Args:
        df: Input DataFrame
        columns: Columns to check for outliers (default: all numeric)
        method: Detection method (iqr, zscore)
        threshold: Threshold for outlier detection
        
    Returns:
        DataFrame with outlier indicators
    """
    try:
        if columns is None:
            columns = df.select_dtypes(include=[np.number]).columns.tolist()
        
        outlier_df = df.copy()
        
        for col in columns:
            if col not in df.columns:
                continue
                
            if method == "iqr":
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - threshold * IQR
                upper = Q3 + threshold * IQR
                outlier_df[f"{col}_outlier"] = (df[col] < lower) | (df[col] > upper)
                
            elif method == "zscore":
                z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
                outlier_df[f"{col}_outlier"] = z_scores > threshold
                
        logger.info(
            "Outlier detection completed",
            method=method,
            columns=columns,
            threshold=threshold
        )
        
        return outlier_df
        
    except Exception as e:
        logger.error("Failed to detect outliers", error=str(e))
        raise