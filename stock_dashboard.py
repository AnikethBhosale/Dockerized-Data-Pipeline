#!/usr/bin/env python3
"""
Stock Market Dashboard
A comprehensive Streamlit dashboard for analyzing stock data from PostgreSQL
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from sqlalchemy import create_engine, text
import os
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page configuration
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .refresh-button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        cursor: pointer;
    }
    .stButton > button {
        background-color: #28a745;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 0.25rem;
        font-weight: bold;
    }
    .stButton > button:hover {
        background-color: #218838;
        color: white;
    }
</style>
""", unsafe_allow_html=True)

class StockDashboard:
    def __init__(self):
        self.engine = None
        self.connect_database()
    
    def connect_database(self):
        """Connect to PostgreSQL database"""
        try:
            # Connect to the stock_data database (where we created the table)
            db_url = (
                f"postgresql://postgres:admin@localhost:5432/stock_data"
            )
            self.engine = create_engine(db_url)
            
            # Test connection
            with self.engine.connect() as conn:
                # Test if we can query the table
                result = conn.execute(text("SELECT COUNT(*) FROM stock_data"))
                count = result.scalar()
                print(f"✅ Connected to stock_data database - {count} records found")
                    
        except Exception as e:
            st.error(f"Database connection failed: {str(e)}")
            st.info("Make sure your Docker containers are running and PostgreSQL is accessible")
            st.info("Try running: docker-compose ps")
    
    def get_stock_data(self, symbol=None):
        """Fetch stock data from database"""
        try:
            query = "SELECT * FROM stock_data WHERE 1=1"
            params = {}
            
            if symbol:
                query += " AND symbol = %(symbol)s"
                params['symbol'] = symbol
            
            query += " ORDER BY timestamp DESC"
            
            df = pd.read_sql(query, self.engine, params=params)
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")
            return pd.DataFrame()
    
    def get_summary_stats(self):
        """Get summary statistics"""
        try:
            with self.engine.connect() as conn:
                # Total records
                result = conn.execute(text("SELECT COUNT(*) FROM stock_data"))
                total_records = result.scalar()
                
                # Records by symbol
                result = conn.execute(text("SELECT symbol, COUNT(*) as count FROM stock_data GROUP BY symbol"))
                symbol_counts = dict(result.fetchall())
                
                # Date range
                result = conn.execute(text("SELECT MIN(timestamp), MAX(timestamp) FROM stock_data"))
                min_date, max_date = result.fetchone()
                
                return {
                    'total_records': total_records,
                    'symbol_counts': symbol_counts,
                    'date_range': (min_date, max_date)
                }
        except Exception as e:
            st.error(f"Error getting summary stats: {str(e)}")
            return {}
    
    def create_price_chart(self, df, symbol):
        """Create interactive price chart"""
        if df.empty:
            return go.Figure()
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=(f'{symbol} Stock Price', 'Volume'),
            row_width=[0.7, 0.3]
        )
        
        # Price line
        fig.add_trace(
            go.Scatter(
                x=df['timestamp'],
                y=df['close_price'],
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4', width=2)
            ),
            row=1, col=1
        )
        
        # Volume bars
        fig.add_trace(
            go.Bar(
                x=df['timestamp'],
                y=df['volume'],
                name='Volume',
                marker_color='#ff7f0e',
                opacity=0.7
            ),
            row=2, col=1
        )
        
        fig.update_layout(
            title=f'{symbol} Stock Analysis',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            height=600,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig
    
    def create_candlestick_chart(self, df, symbol):
        """Create candlestick chart"""
        if df.empty:
            return go.Figure()
        
        fig = go.Figure(data=[go.Candlestick(
            x=df['timestamp'],
            open=df['open_price'],
            high=df['high_price'],
            low=df['low_price'],
            close=df['close_price'],
            name=symbol
        )])
        
        fig.update_layout(
            title=f'{symbol} Candlestick Chart',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            height=500
        )
        
        return fig
    
    def create_technical_indicators(self, df, symbol):
        """Create technical indicators chart"""
        if df.empty:
            return go.Figure()
        
        # Calculate moving averages
        df['SMA_20'] = df['close_price'].rolling(window=20).mean()
        df['SMA_50'] = df['close_price'].rolling(window=50).mean()
        
        # Calculate RSI
        delta = df['close_price'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        fig = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            subplot_titles=(f'{symbol} Price with Moving Averages', 'RSI', 'Volume'),
            row_width=[0.5, 0.25, 0.25]
        )
        
        # Price and moving averages
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['close_price'], name='Close Price', line=dict(color='#1f77b4')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['SMA_20'], name='SMA 20', line=dict(color='#ff7f0e')),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['SMA_50'], name='SMA 50', line=dict(color='#2ca02c')),
            row=1, col=1
        )
        
        # RSI
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['RSI'], name='RSI', line=dict(color='#d62728')),
            row=2, col=1
        )
        fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
        fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # Volume
        fig.add_trace(
            go.Bar(x=df['timestamp'], y=df['volume'], name='Volume', marker_color='#9467bd'),
            row=3, col=1
        )
        
        fig.update_layout(height=800, showlegend=True)
        
        return fig
    
    def create_correlation_heatmap(self, df):
        """Create correlation heatmap between stocks"""
        if df.empty:
            return go.Figure()
        
        # Pivot data to get close prices by symbol
        pivot_df = df.pivot(index='timestamp', columns='symbol', values='close_price')
        
        # Calculate correlation matrix
        corr_matrix = pivot_df.corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            textfont={"size": 10}
        ))
        
        fig.update_layout(
            title='Stock Correlation Heatmap',
            height=500,
            xaxis_title='Stocks',
            yaxis_title='Stocks'
        )
        
        return fig
    
    def create_volume_analysis(self, df, symbol):
        """Create volume analysis chart"""
        if df.empty:
            return go.Figure()
        
        # Calculate volume moving average
        df['Volume_MA'] = df['volume'].rolling(window=20).mean()
        
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.1,
            subplot_titles=(f'{symbol} Volume Analysis', 'Price vs Volume'),
            row_width=[0.6, 0.4]
        )
        
        # Volume with moving average
        fig.add_trace(
            go.Bar(x=df['timestamp'], y=df['volume'], name='Volume', marker_color='#ff7f0e'),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['Volume_MA'], name='Volume MA (20)', line=dict(color='red')),
            row=1, col=1
        )
        
        # Price vs Volume scatter
        fig.add_trace(
            go.Scatter(
                x=df['close_price'],
                y=df['volume'],
                mode='markers',
                name='Price vs Volume',
                marker=dict(color=df['close_price'], colorscale='Viridis', size=8)
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=700, showlegend=True)
        
        return fig

def main():
    st.markdown('<h1 class="main-header">📈 Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Initialize dashboard
    dashboard = StockDashboard()
    
    if not dashboard.engine:
        st.error("Cannot connect to database. Please check your Docker containers.")
        return
    
    # Sidebar for controls
    st.sidebar.header("🎛️ Dashboard Controls")
    
    # Manual refresh button with session state
    if 'refresh_counter' not in st.session_state:
        st.session_state.refresh_counter = 0
    
    if st.sidebar.button("🔄 Refresh Dashboard", type="primary"):
        st.session_state.refresh_counter += 1
        st.rerun()
    
    st.sidebar.markdown(f"**Last Refresh:** {st.session_state.refresh_counter}")
    st.sidebar.markdown("---")
    
    # Get summary statistics
    summary = dashboard.get_summary_stats()
    
    if summary:
        # Display summary metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Records", f"{summary['total_records']:,}")
        
        with col2:
            st.metric("Stocks Tracked", len(summary['symbol_counts']))
        
        with col3:
            st.metric("Last Updated", datetime.now().strftime("%H:%M:%S"))
        
        st.markdown("---")
        
        # Stock selection
        available_symbols = list(summary['symbol_counts'].keys())
        selected_symbol = st.sidebar.selectbox("Select Stock Symbol", available_symbols)
        
        # Fetch data
        df = dashboard.get_stock_data(selected_symbol)
        
        if not df.empty:
            # Display data summary
            st.subheader(f"📊 {selected_symbol} Data Summary")
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Records", len(df))
            with col2:
                st.metric("Current Price", f"${df['close_price'].iloc[0]:.2f}")
            with col3:
                price_change = df['close_price'].iloc[0] - df['close_price'].iloc[-1]
                st.metric("Price Change", f"${price_change:.2f}")
            with col4:
                st.metric("Avg Volume", f"{df['volume'].mean():,.0f}")
            
            st.markdown("---")
            
            # Display multiple charts by default
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader(f"📈 {selected_symbol} Price Chart")
                fig = dashboard.create_price_chart(df, selected_symbol)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader(f"🕯️ {selected_symbol} Candlestick Chart")
                fig = dashboard.create_candlestick_chart(df, selected_symbol)
                st.plotly_chart(fig, use_container_width=True)
            
            # Technical Indicators (full width)
            st.subheader(f"🔧 {selected_symbol} Technical Indicators")
            fig = dashboard.create_technical_indicators(df, selected_symbol)
            st.plotly_chart(fig, use_container_width=True)
            
            # Correlation Heatmap for all symbols
            st.subheader("🔥 Stock Correlation Heatmap")
            all_df = dashboard.get_stock_data()
            fig = dashboard.create_correlation_heatmap(all_df)
            st.plotly_chart(fig, use_container_width=True)
            
            # Display raw data
            st.subheader("📋 Raw Data")
            st.dataframe(df.head(20), use_container_width=True)
            
        else:
            st.warning(f"No data found for {selected_symbol} in the selected date range.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        """
        <div style='text-align: center; color: #666;'>
            <p>📊 Stock Market Dashboard | Data from PostgreSQL | Built with Streamlit & Plotly</p>
            <p>Last refresh: {}</p>
        </div>
        """.format(datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()
