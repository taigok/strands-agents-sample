#!/bin/bash

echo "🤖 Starting Strands Multi-Agent System"
echo "=================================="

# Check if required files exist
if [ ! -f "demo_app.py" ]; then
    echo "❌ demo_app.py not found!"
    exit 1
fi

if [ ! -f "sample_data.csv" ]; then
    echo "❌ sample_data.csv not found!"
    exit 1
fi

# Test the system first
echo "🧪 Running system tests..."
python demo_cli.py status

if [ $? -ne 0 ]; then
    echo "❌ System check failed!"
    exit 1
fi

echo "✅ System check passed!"
echo ""

# Install any missing dependencies
echo "📦 Checking dependencies..."
pip install -q streamlit pandas plotly structlog pydantic pydantic-settings python-dotenv

# Start Streamlit
echo "🚀 Starting Streamlit application..."
echo "🌐 The app will be available at: http://localhost:8501"
echo "📋 Check VS Code PORTS tab if running in devcontainer"
echo ""

# Start with proper configuration
streamlit run demo_app.py \
    --server.port 8501 \
    --server.address 0.0.0.0 \
    --server.headless true \
    --browser.gatherUsageStats false \
    --server.enableCORS false \
    --server.enableXsrfProtection false