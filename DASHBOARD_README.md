# 📊 Stock Market Dashboard

A comprehensive, interactive dashboard for analyzing stock market data from your PostgreSQL database. Built with Streamlit and Plotly for beautiful, interactive visualizations.

## 🚀 Features

### 📈 **Chart Types Available**
1. **Price Chart** - Line chart with volume bars
2. **Candlestick Chart** - OHLC (Open, High, Low, Close) visualization
3. **Technical Indicators** - Moving averages, RSI, volume analysis
4. **Volume Analysis** - Volume trends and price-volume relationships
5. **Correlation Heatmap** - Stock relationship analysis

### 🎛️ **Interactive Controls**
- **Manual Refresh Button** - Update data on demand
- **Stock Symbol Selection** - Choose which stock to analyze
- **Date Range Picker** - Customize time periods
- **Chart Type Selector** - Switch between different visualizations

### 📊 **Real-time Data**
- **Live Database Connection** - Direct PostgreSQL access
- **Summary Metrics** - Key statistics and insights
- **Raw Data View** - Access to underlying data

## 🛠️ Setup Instructions

### **Prerequisites**
- Python 3.8 or higher
- Your PostgreSQL database running (from the main pipeline)
- Docker containers running (if using the main project)

### **Option 1: Quick Start (Recommended)**

1. **Install dependencies:**
   ```bash
   pip install -r dashboard_requirements.txt
   ```

2. **Launch dashboard:**
   ```bash
   python run_dashboard.py
   ```

3. **Open browser:**
   Navigate to http://localhost:8501

### **Option 2: Manual Launch**

1. **Install dependencies:**
   ```bash
   pip install -r dashboard_requirements.txt
   ```

2. **Run Streamlit:**
   ```bash
   streamlit run stock_dashboard.py --server.port=8501
   ```

### **Option 3: Using the Launcher Script**

1. **Make script executable (Linux/Mac):**
   ```bash
   chmod +x run_dashboard.py
   ```

2. **Run the launcher:**
   ```bash
   python run_dashboard.py
   ```

## 🔧 Configuration

### **Database Connection**
The dashboard automatically connects to your PostgreSQL database using these default settings:
- **Host**: localhost
- **Port**: 5432
- **Database**: stock_data
- **Username**: postgres
- **Password**: admin123

### **Environment Variables**
You can override defaults by setting these environment variables:
```bash
export POSTGRES_HOST=your_host
export POSTGRES_DB=your_database
export POSTGRES_USER=your_username
export POSTGRES_PASSWORD=your_password
```

## 📊 How to Use

### **1. Dashboard Overview**
- **Summary Metrics**: View total records, stocks tracked, and data range
- **Stock Selection**: Choose which stock symbol to analyze
- **Date Range**: Select custom time periods for analysis

### **2. Chart Navigation**
- **Chart Type Dropdown**: Select from 5 different chart types
- **Interactive Charts**: Zoom, pan, and hover over data points
- **Responsive Design**: Charts adapt to different screen sizes

### **3. Data Analysis**
- **Price Trends**: Analyze stock price movements over time
- **Volume Analysis**: Understand trading volume patterns
- **Technical Indicators**: Use RSI and moving averages for insights
- **Correlation Analysis**: See relationships between different stocks

## 🎯 Chart Types Explained

### **Price Chart**
- **Upper Panel**: Stock price line chart
- **Lower Panel**: Trading volume bars
- **Features**: Interactive tooltips, zoom capabilities

### **Candlestick Chart**
- **Green Candles**: Price closed higher than opened
- **Red Candles**: Price closed lower than opened
- **Wicks**: Show high and low prices for the period

### **Technical Indicators**
- **Moving Averages**: 20-day and 50-day simple moving averages
- **RSI (Relative Strength Index)**: Momentum indicator (30=oversold, 70=overbought)
- **Volume**: Trading volume with 20-day moving average

### **Volume Analysis**
- **Volume Trends**: Bar chart showing trading volume over time
- **Price vs Volume**: Scatter plot showing relationship between price and volume
- **Volume Moving Average**: Trend line for volume analysis

### **Correlation Heatmap**
- **Color Scale**: Red (negative correlation) to Blue (positive correlation)
- **Values**: Correlation coefficients between -1 and 1
- **Insights**: Identify which stocks move together

## 🔄 Manual Refresh

### **Refresh Button**
- **Location**: Top of the left sidebar
- **Function**: Manually update all data from the database
- **Counter**: Shows how many times you've refreshed

### **When to Refresh**
- After running the pipeline to get new data
- When you want to see the latest database state
- If you suspect data might be stale

## 🐛 Troubleshooting

### **Database Connection Issues**
```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# Verify database is accessible
docker-compose exec postgres psql -U postgres -d stock_data -c "SELECT 1"
```

### **Missing Dependencies**
```bash
# Install requirements
pip install -r dashboard_requirements.txt

# Or install individually
pip install streamlit plotly pandas psycopg2-binary sqlalchemy
```

### **Port Already in Use**
```bash
# Check what's using port 8501
netstat -an | findstr :8501

# Kill the process or use a different port
streamlit run stock_dashboard.py --server.port=8502
```

## 📱 System Requirements

- **Memory**: Minimum 4GB RAM (8GB recommended)
- **Storage**: 1GB free space
- **Browser**: Modern browser with JavaScript enabled
- **Network**: Access to localhost:8501

## 🔒 Security Notes

- **Local Access Only**: Dashboard runs on localhost by default
- **Database Credentials**: Stored in environment variables
- **No External Access**: All data stays on your local machine

## 🚀 Performance Tips

- **Refresh Strategically**: Only refresh when you need new data
- **Use Date Ranges**: Limit data to specific time periods for faster loading
- **Close Unused Tabs**: Streamlit uses memory for each chart

## 📞 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your database is running and accessible
3. Ensure all dependencies are installed
4. Check the Streamlit logs for error messages

## 🎉 Success Indicators

You'll know the dashboard is working when:
- ✅ http://localhost:8501 opens in your browser
- ✅ Charts display with your stock data
- ✅ Database connection shows no errors
- ✅ Refresh button updates data successfully

---

**Happy Stock Analysis! 📈📊**
