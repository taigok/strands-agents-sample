import os
from typing import Optional, Dict, Any
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    # AWS Configuration
    aws_region: str = Field(default="us-east-1", env="AWS_DEFAULT_REGION")
    aws_access_key_id: Optional[str] = Field(default=None, env="AWS_ACCESS_KEY_ID")
    aws_secret_access_key: Optional[str] = Field(default=None, env="AWS_SECRET_ACCESS_KEY")
    
    # Bedrock Configuration
    bedrock_model_id: str = Field(
        default="anthropic.claude-3-5-sonnet-20241022-v2:0",
        env="BEDROCK_MODEL_ID"
    )
    bedrock_endpoint_url: Optional[str] = Field(default=None, env="BEDROCK_ENDPOINT_URL")
    
    # Agent Configuration
    agent_max_iterations: int = Field(default=10, env="AGENT_MAX_ITERATIONS")
    agent_timeout_seconds: int = Field(default=300, env="AGENT_TIMEOUT_SECONDS")
    agent_memory_type: str = Field(default="conversation_buffer", env="AGENT_MEMORY_TYPE")
    
    # Tool Configuration
    tool_timeout_seconds: int = Field(default=30, env="TOOL_TIMEOUT_SECONDS")
    max_file_size_mb: int = Field(default=100, env="MAX_FILE_SIZE_MB")
    
    # Observability
    langfuse_public_key: Optional[str] = Field(default=None, env="LANGFUSE_PUBLIC_KEY")
    langfuse_secret_key: Optional[str] = Field(default=None, env="LANGFUSE_SECRET_KEY")
    langfuse_host: str = Field(default="https://cloud.langfuse.com", env="LANGFUSE_HOST")
    enable_tracing: bool = Field(default=True, env="ENABLE_TRACING")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # API Keys for external services
    serpapi_key: Optional[str] = Field(default=None, env="SERPAPI_KEY")
    openweather_api_key: Optional[str] = Field(default=None, env="OPENWEATHER_API_KEY")
    
    # Application Settings
    app_name: str = Field(default="Strands Multi-Agent System", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # Streamlit Configuration
    streamlit_port: int = Field(default=8501, env="STREAMLIT_PORT")
    streamlit_theme: str = Field(default="dark", env="STREAMLIT_THEME")
    
    # Storage Configuration
    s3_bucket_name: Optional[str] = Field(default=None, env="S3_BUCKET_NAME")
    local_storage_path: str = Field(default="/tmp/strands-storage", env="LOCAL_STORAGE_PATH")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
    
    def get_bedrock_config(self) -> Dict[str, Any]:
        """Get Bedrock client configuration"""
        config = {
            "region_name": self.aws_region,
            "model_id": self.bedrock_model_id,
        }
        
        if self.bedrock_endpoint_url:
            config["endpoint_url"] = self.bedrock_endpoint_url
            
        if self.aws_access_key_id and self.aws_secret_access_key:
            config["aws_access_key_id"] = self.aws_access_key_id
            config["aws_secret_access_key"] = self.aws_secret_access_key
            
        return config
    
    def get_langfuse_config(self) -> Optional[Dict[str, Any]]:
        """Get Langfuse configuration if available"""
        if not self.enable_tracing:
            return None
            
        if self.langfuse_public_key and self.langfuse_secret_key:
            return {
                "public_key": self.langfuse_public_key,
                "secret_key": self.langfuse_secret_key,
                "host": self.langfuse_host,
            }
        return None
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment"""
        return self.environment.lower() == "production"
    
    @property
    def max_file_size_bytes(self) -> int:
        """Get max file size in bytes"""
        return self.max_file_size_mb * 1024 * 1024


# Create a singleton instance
settings = Settings()