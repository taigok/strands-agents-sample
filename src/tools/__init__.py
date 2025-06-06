"""
Custom tools for the Multi-Agent System
"""

from .data_tools import (
    load_csv_file,
    load_excel_file,
    analyze_dataframe,
    filter_dataframe,
    aggregate_dataframe,
    pivot_dataframe,
    export_dataframe,
    detect_outliers
)

from .search_tools import (
    web_search,
    fetch_webpage_content,
    fetch_multiple_urls,
    search_academic_papers,
    extract_structured_data,
    search_company_info,
    verify_facts
)

from .document_tools import (
    create_pdf_report,
    create_word_document,
    create_html_report,
    merge_documents,
    extract_text_from_pdf,
    create_template_document
)

__all__ = [
    # Data tools
    "load_csv_file",
    "load_excel_file",
    "analyze_dataframe",
    "filter_dataframe",
    "aggregate_dataframe",
    "pivot_dataframe",
    "export_dataframe",
    "detect_outliers",
    
    # Search tools
    "web_search",
    "fetch_webpage_content",
    "fetch_multiple_urls",
    "search_academic_papers",
    "extract_structured_data",
    "search_company_info",
    "verify_facts",
    
    # Document tools
    "create_pdf_report",
    "create_word_document",
    "create_html_report",
    "merge_documents",
    "extract_text_from_pdf",
    "create_template_document"
]