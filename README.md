# 📈 Dockerized Data Pipeline with Dagster

A comprehensive, production-ready data pipeline that automatically fetches, processes, and stores stock market data using **Dagster** as the orchestrator. This project demonstrates modern data engineering practices with Docker containerization, robust error handling, and includes an interactive dashboard for data visualization.

## 🎯 Project Overview

This project implements a complete data pipeline solution that:

- **Fetches real-time stock data** from Alpha Vantage API
- **Processes and parses** JSON responses into structured data
- **Stores data** in PostgreSQL with conflict resolution
- **Orchestrates workflows** using Dagster
- **Provides monitoring** through Dagster UI
- **Includes a beautiful dashboard** for data visualization and analysis

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Alpha Vantage │    │     Dagster     │    │   PostgreSQL    │
│      API        │───▶│   Orchestrator  │───▶│    Database     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │  Streamlit      │
                       │  Dashboard      │
                       └─────────────────┘
```

## ✨ Key Features

### 🔄 **Dual-Mode Operation**
- **Dagster Orchestrated**: Automated, scheduled data pipeline execution
- **Standalone Execution**: Manual data fetching and processing
- **Flexible Configuration**: Easy switching between modes

### 🛡️ **Robust Error Handling**
- **API Error Management**: Graceful handling of rate limits and failures
- **Database Resilience**: Connection retry logic and conflict resolution
- **Data Validation**: Comprehensive data quality checks
- **Retry Policies**: Automatic retry mechanisms for failed operations

### 📊 **Interactive Dashboard**
- **Real-time Data Visualization**: Live charts and metrics
- **Multiple Chart Types**: Price charts, candlestick, technical indicators
- **Stock Correlation Analysis**: Heatmaps and correlation matrices
- **Manual Refresh**: On-demand data updates
- **Responsive Design**: Beautiful, modern UI

### 🔧 **Production-Ready Features**
- **Docker Containerization**: Complete environment isolation
- **Environment Variables**: Secure credential management
- **Health Checks**: Service monitoring and validation
- **Data Persistence**: Docker volumes for data durability
- **Scalable Design**: Easy to extend and modify

## 🚀 Quick Start

### Prerequisites

- **Docker & Docker Compose** (latest version)
- **Alpha Vantage API Key** (free at [alphavantage.co](https://www.alphavantage.co/support/#api-key))

### 1. Clone and Setup

```bash
git clone <repository-url>
cd Dockerized-Data-Pipeline
```

### 2. Configure Environment

```bash
# Copy environment template
cp env.example .env

# Edit .env file with your API key
# ALPHA_VANTAGE_API_KEY=your_api_key_here
```

### 3. Start the Pipeline

```bash
# Option 1: Use the automated startup script
chmod +x start.sh
./start.sh

# Option 2: Manual startup
docker-compose up --build -d
```

### 4. Access Services

- **Dagster UI**: http://localhost:3000
- **PostgreSQL**: localhost:5432
- **Dashboard**: http://localhost:8501 (after running dashboard)

## 📋 Detailed Setup Instructions

### Environment Configuration

The project uses environment variables for secure configuration:

```bash
# Required: Alpha Vantage API Key
ALPHA_VANTAGE_API_KEY=your_api_key_here

# Optional: Database Configuration (defaults provided)
POSTGRES_USER=postgres
POSTGRES_PASSWORD=admin
POSTGRES_DB=stock_data
POSTGRES_HOST=postgres
```

### Database Schema

The pipeline creates a comprehensive `stock_data` table:

```sql
CREATE TABLE stock_data (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(10) NOT NULL,
    timestamp TIMESTAMP NOT NULL,
    open_price DECIMAL(10,4),
    high_price DECIMAL(10,4),
    low_price DECIMAL(10,4),
    close_price DECIMAL(10,4),
    volume BIGINT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(symbol, timestamp)
);
```

### Running the Pipeline

#### Method 1: Dagster UI (Recommended)

1. Open http://localhost:3000
2. Navigate to the "Assets" tab
3. Find `stock_data_pipeline` asset
4. Click "Materialize" to execute the pipeline
5. Monitor execution in real-time

#### Method 2: Standalone Script

```bash
# Run with default symbols (IBM, MSFT)
python stock_pipeline/data_fetcher.py

# Run with custom symbols
python stock_pipeline/data_fetcher.py --symbols AAPL,GOOGL,MSFT

# Run with custom interval
python stock_pipeline/data_fetcher.py --interval 15min
```

## 📊 Dashboard Setup

### Launch the Dashboard

```bash
# Install dashboard dependencies
pip install -r dashboard_requirements.txt

# Run the dashboard
python run_dashboard.py
```

### Dashboard Features

- **📈 Price Charts**: Interactive line charts with volume
- **🕯️ Candlestick Charts**: Traditional OHLC visualization
- **🔧 Technical Indicators**: SMA, RSI, and volume analysis
- **🔥 Correlation Heatmaps**: Stock correlation analysis
- **📋 Raw Data Tables**: Detailed data inspection
- **🔄 Manual Refresh**: Real-time data updates

## 🏗️ Project Structure

```
Dockerized-Data-Pipeline/
├── docker-compose.yml          # Main orchestration file
├── Dockerfile                  # Dagster container definition
├── requirements.txt            # Python dependencies
├── init.sql                   # Database schema
├── workspace.yaml             # Dagster workspace config
├── env.example                # Environment template
├── start.sh                   # Automated startup script
│
├── stock_pipeline/            # Core pipeline code
│   ├── __init__.py
│   ├── stock_pipeline.py      # Dagster assets and jobs
│   └── data_fetcher.py        # Standalone data fetcher
│
├── stock_dashboard.py         # Streamlit dashboard
├── run_dashboard.py           # Dashboard launcher
├── dashboard_requirements.txt # Dashboard dependencies
│
├── test_*.py                  # Testing and validation scripts
└── README.md                  # This file
```

## 🔧 Technical Implementation

### Dagster Pipeline (`stock_pipeline.py`)

The core pipeline implements:

- **Asset Definition**: `@asset` decorator for data pipeline
- **Configuration Management**: Pydantic-based config validation
- **Error Handling**: Comprehensive try-catch blocks
- **Retry Policies**: Automatic retry on failures
- **Logging**: Structured logging throughout

### Data Fetching (`data_fetcher.py`)

Standalone script with:

- **API Integration**: Alpha Vantage API client
- **Data Parsing**: JSON to DataFrame conversion
- **Database Operations**: SQLAlchemy ORM usage
- **Conflict Resolution**: UPSERT operations
- **Command-line Interface**: Flexible execution options

### Database Management

- **Connection Pooling**: Efficient database connections
- **Transaction Management**: ACID compliance
- **Indexing**: Optimized query performance
- **Triggers**: Automatic timestamp updates

## 🛡️ Error Handling & Resilience

### API Error Management

```python
# Rate limit handling
if 'Note' in data:
    logger.warning(f"API Rate Limit: {data['Note']}")
    return {}

# API error detection
if 'Error Message' in data:
    raise Exception(f"API Error: {data['Error Message']}")
```

### Database Resilience

```python
# Connection retry logic
@retry_policy(max_retries=3, delay=60)
def insert_stock_data(self, data: pd.DataFrame) -> int:
    # Implementation with error handling
```

### Data Validation

- **Type Checking**: Ensures data type consistency
- **Range Validation**: Validates price and volume ranges
- **Null Handling**: Graceful handling of missing data
- **Duplicate Prevention**: Unique constraint enforcement

## 📈 Monitoring & Observability

### Dagster UI Features

- **Asset Lineage**: Visual pipeline dependencies
- **Execution History**: Complete run history
- **Real-time Logs**: Live execution monitoring
- **Performance Metrics**: Execution time tracking
- **Error Reporting**: Detailed error analysis

### Dashboard Metrics

- **Data Summary**: Total records and symbols tracked
- **Real-time Updates**: Live data refresh capabilities
- **Performance Indicators**: Technical analysis tools
- **Correlation Analysis**: Multi-stock relationships

## 🔄 Data Persistence

### Docker Volumes

The project uses Docker volumes for data persistence:

```yaml
volumes:
  postgres_data:    # PostgreSQL data persistence
  dagster_home:     # Dagster metadata persistence
```

### Volume Locations

- **PostgreSQL Data**: `/var/lib/postgresql/data`
- **Dagster Metadata**: `/opt/dagster/dagster_home`

### Data Durability

- **Automatic Backups**: Database data persists across container restarts
- **Metadata Preservation**: Dagster execution history maintained
- **Configuration Persistence**: Environment settings preserved

## 🚀 Scaling & Performance

### Horizontal Scaling

- **Multi-container Architecture**: Separate services for different components
- **Load Balancing**: Ready for multiple Dagster workers
- **Database Optimization**: Indexed queries for performance

### Performance Optimizations

- **Connection Pooling**: Efficient database connections
- **Batch Processing**: Bulk data operations
- **Caching**: Dagster asset caching
- **Parallel Execution**: Concurrent symbol processing

## 🔒 Security Features

### Environment Variables

- **API Key Management**: Secure credential storage
- **Database Credentials**: Encrypted connection strings
- **No Hardcoded Secrets**: All sensitive data externalized

### Network Security

- **Container Isolation**: Service-to-service communication
- **Port Management**: Controlled service exposure
- **Health Checks**: Service validation

## 🧪 Testing & Validation

### Built-in Testing Scripts

```bash
# Test database connection
python test_setup.py

# Test data pipeline
python test_data.py

# Test database connectivity
python test_db_connection.py

# Check database contents
python check_database.py
```

### Validation Features

- **Connection Testing**: Database connectivity validation
- **Data Integrity**: Record count verification
- **API Testing**: Endpoint availability checks
- **Pipeline Validation**: Complete workflow testing

## 🛠️ Troubleshooting

### Common Issues

1. **Docker Not Running**
   ```bash
   docker info
   # Start Docker Desktop if needed
   ```

2. **Port Conflicts**
   ```bash
   # Check port usage
   netstat -an | grep :3000
   netstat -an | grep :5432
   ```

3. **API Rate Limits**
   ```bash
   # Check API key in .env file
   cat .env | grep ALPHA_VANTAGE_API_KEY
   ```

4. **Database Connection Issues**
   ```bash
   # Check container status
   docker-compose ps
   
   # View logs
   docker-compose logs postgres
   ```

### Debug Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f dagster

# Check container status
docker-compose ps

# Restart services
docker-compose restart

# Clean restart
docker-compose down -v
docker-compose up --build -d
```

## 📚 API Documentation

### Alpha Vantage API

- **Endpoint**: `https://www.alphavantage.co/query`
- **Function**: `TIME_SERIES_INTRADAY`
- **Intervals**: 1min, 5min, 15min, 30min, 60min
- **Rate Limits**: 5 calls per minute, 500 per day (free tier)

### Supported Stock Symbols

- **Default**: IBM, MSFT
- **Customizable**: Any valid stock symbol
- **Batch Processing**: Multiple symbols in single run

## 🤝 Contributing

### Development Setup

1. **Fork the repository**
2. **Create feature branch**
3. **Make changes**
4. **Test thoroughly**
5. **Submit pull request**

### Code Standards

- **Python**: PEP 8 compliance
- **Documentation**: Comprehensive docstrings
- **Testing**: Unit tests for new features
- **Error Handling**: Robust exception management

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **Alpha Vantage**: Free stock market data API
- **Dagster**: Modern data orchestration platform
- **Streamlit**: Interactive web application framework
- **PostgreSQL**: Robust relational database
- **Docker**: Containerization platform



