#!/bin/bash

# Stock Data Pipeline Startup Script

echo "🚀 Starting Stock Data Pipeline Setup"
echo "======================================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp env.example .env
    echo "⚠️  Please edit .env file and add your Alpha Vantage API key"
    echo "   Get a free API key at: https://www.alphavantage.co/support/#api-key"
    echo ""
    echo "Press Enter when you've updated the .env file..."
    read
fi

# Check if API key is set
if grep -q "your_api_key_here" .env; then
    echo "⚠️  Please update your Alpha Vantage API key in the .env file"
    echo "   Current value: your_api_key_here"
    echo ""
    echo "Press Enter when you've updated the API key..."
    read
fi

echo "🔧 Building and starting services..."
docker-compose up --build -d

echo "⏳ Waiting for services to start..."
sleep 10

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    echo "✅ Services are running!"
    echo ""
    echo "🌐 Access your pipeline:"
    echo "   Dagster UI: http://localhost:3000"
    echo "   PostgreSQL: localhost:5432"
    echo ""
    echo "📊 To run the pipeline:"
    echo "   1. Open http://localhost:3000"
    echo "   2. Go to Assets tab"
    echo "   3. Click 'Materialize' on stock_data_pipeline"
    echo ""
    echo "🔍 To view logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 To stop services:"
    echo "   docker-compose down"
else
    echo "❌ Services failed to start. Check logs with:"
    echo "   docker-compose logs"
    exit 1
fi
