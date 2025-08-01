"""
Streamlit Dashboard for E-commerce Analytics
Interactive dashboard with all analytics features
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_processing import EcommerceDataProcessor
from analytics import EcommerceAnalytics
from forecasting import RevenueForecaster

# Page configuration
st.set_page_config(
    page_title="E-commerce Analytics Dashboard",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .sidebar .sidebar-content {
        background-color: #f8f9fa;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load and cache the processed data"""
    processor = EcommerceDataProcessor()
    
    # Try to load processed data first
    cleaned_df = processor.load_processed_data()
    
    if cleaned_df is None:
        # If no processed data, load and clean raw data
        raw_df = processor.load_data()
        if raw_df is None:
            st.error("[ERROR] Data file not found. Please download the UCI Online Retail Dataset and place it in the data/ folder.")
            st.info("Download from: https://archive.ics.uci.edu/ml/datasets/online+retail")
            return None, None, None
        
        cleaned_df = processor.clean_data()
        if cleaned_df is None:
            st.error("[ERROR] Error cleaning data.")
            return None, None, None
    
    # Initialize analytics and forecasting
    analytics = EcommerceAnalytics(processor)
    forecaster = RevenueForecaster(processor)
    
    return processor, analytics, forecaster

def main():
    """Main dashboard function"""
    
    # Header
    st.markdown('<h1 class="main-header">🛒 E-commerce Analytics Dashboard</h1>', unsafe_allow_html=True)
    
    # Load data
    with st.spinner("Loading data and running analytics..."):
        processor, analytics, forecaster = load_data()
    
    if processor is None:
        st.stop()
    
    # Sidebar filters
    st.sidebar.header("[INFO] Dashboard Filters")
    
    # Date range filter
    if processor.cleaned_df is not None:
        min_date = processor.cleaned_df['InvoiceDate'].min().date()
        max_date = processor.cleaned_df['InvoiceDate'].max().date()
        
        date_range = st.sidebar.date_input(
            "Select Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )
        
        # Filter data based on date range
        if len(date_range) == 2:
            filtered_df = processor.cleaned_df[
                (processor.cleaned_df['InvoiceDate'].dt.date >= date_range[0]) &
                (processor.cleaned_df['InvoiceDate'].dt.date <= date_range[1])
            ]
        else:
            filtered_df = processor.cleaned_df
    else:
        filtered_df = None
    
    # Main content
    if filtered_df is not None:
        # Calculate KPIs
        kpis = processor.calculate_kpis()
        
        # Display KPIs
        st.subheader("📈 Key Performance Indicators")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Total Revenue",
                f"${kpis['total_revenue']:,.0f}",
                f"{kpis['revenue_growth_pct']:.1f}%"
            )
        
        with col2:
            st.metric(
                "Total Customers",
                f"{kpis['total_customers']:,}",
                f"{kpis['total_customers']/1000:.1f}K"
            )
        
        with col3:
            st.metric(
                "Total Orders",
                f"{kpis['total_orders']:,}",
                f"{kpis['total_orders']/1000:.1f}K"
            )
        
        with col4:
            st.metric(
                "Avg Order Value",
                f"${kpis['avg_order_value']:.2f}",
                f"{kpis['avg_items_per_order']:.1f} items"
            )
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Revenue Analysis", 
            "👥 Customer Insights", 
            "📦 Product Performance", 
            "📈 Forecasting", 
            "🌍 Geographic Analysis"
        ])
        
        with tab1:
            display_revenue_analysis(processor, forecaster)
        
        with tab2:
            display_customer_insights(analytics)
        
        with tab3:
            display_product_performance(analytics)
        
        with tab4:
            display_forecasting(forecaster)
        
        with tab5:
            display_geographic_analysis(analytics)
        
        # Business Insights Section
        st.subheader("💡 Business Insights & Recommendations")
        
        # Get business report
        if analytics.rfm_data is None:
            analytics.perform_rfm_analysis()
        
        report = analytics.generate_business_report()
        
        if report and 'recommendations' in report:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 🎯 Strategic Recommendations")
                for i, rec in enumerate(report['recommendations'][:3], 1):
                    priority_color = {
                        'High': '🔴',
                        'Medium': '🟡', 
                        'Low': '🟢'
                    }.get(rec['priority'], '⚪')
                    
                    st.markdown(f"""
                    **{priority_color} {rec['category']}**  
                    {rec['recommendation']}  
                    *Expected Impact: {rec['expected_impact']}*
                    """)
            
            with col2:
                st.markdown("### 📊 Key Insights")
                if 'customer_insights' in report:
                    insights = report['customer_insights']
                    st.markdown(f"""
                    - **Top Customer Segment**: {insights.get('top_segment', 'N/A')}
                    - **Champions Count**: {insights.get('champions_count', 0)} customers
                    - **At Risk Customers**: {insights.get('at_risk_count', 0)} customers
                    - **Repeat Customer Rate**: {insights.get('repeat_customer_rate', 0):.1f}%
                    """)
        
    else:
        st.error("No data available for analysis.")

def display_revenue_analysis(processor, forecaster):
    """Display revenue analysis charts"""
    st.subheader("📊 Revenue Trends & Analysis")
    
    # Get monthly metrics
    monthly_metrics = processor.get_monthly_metrics()
    
    if monthly_metrics is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue trend
            fig_revenue = px.line(
                monthly_metrics, 
                x='Month', 
                y='Revenue',
                title='Monthly Revenue Trend',
                labels={'Revenue': 'Revenue ($)', 'Month': 'Date'}
            )
            fig_revenue.update_layout(height=400)
            st.plotly_chart(fig_revenue, use_container_width=True)
        
        with col2:
            # Orders trend
            fig_orders = px.line(
                monthly_metrics, 
                x='Month', 
                y='Orders',
                title='Monthly Orders Trend',
                labels={'Orders': 'Number of Orders', 'Month': 'Date'}
            )
            fig_orders.update_layout(height=400)
            st.plotly_chart(fig_orders, use_container_width=True)
        
        # Seasonal patterns
        st.subheader("📅 Seasonal Patterns")
        
        if processor.cleaned_df is not None:
            # Day of week analysis
            dow_analysis = processor.cleaned_df.groupby('DayName').agg({
                'TotalPrice': 'sum',
                'InvoiceNo': 'nunique'
            }).reset_index()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig_dow = px.bar(
                    dow_analysis,
                    x='DayName',
                    y='TotalPrice',
                    title='Revenue by Day of Week',
                    labels={'TotalPrice': 'Revenue ($)', 'DayName': 'Day'}
                )
                fig_dow.update_layout(height=300)
                st.plotly_chart(fig_dow, use_container_width=True)
            
            with col2:
                # Hour analysis
                hour_analysis = processor.cleaned_df.groupby('Hour').agg({
                    'TotalPrice': 'sum',
                    'InvoiceNo': 'nunique'
                }).reset_index()
                
                fig_hour = px.bar(
                    hour_analysis,
                    x='Hour',
                    y='TotalPrice',
                    title='Revenue by Hour of Day',
                    labels={'TotalPrice': 'Revenue ($)', 'Hour': 'Hour'}
                )
                fig_hour.update_layout(height=300)
                st.plotly_chart(fig_hour, use_container_width=True)

def display_customer_insights(analytics):
    """Display customer insights and RFM analysis"""
    st.subheader("👥 Customer Segmentation & Insights")
    
    # Perform RFM analysis if not already done
    if analytics.rfm_data is None:
        with st.spinner("Performing RFM analysis..."):
            rfm_data = analytics.perform_rfm_analysis()
    else:
        rfm_data = analytics.rfm_data
    
    if rfm_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Customer segments pie chart
            segment_counts = rfm_data['Segment'].value_counts()
            fig_segments = px.pie(
                values=segment_counts.values,
                names=segment_counts.index,
                title='Customer Segmentation',
                hole=0.4
            )
            fig_segments.update_layout(height=400)
            st.plotly_chart(fig_segments, use_container_width=True)
        
        with col2:
            # RFM score distribution
            fig_rfm = px.histogram(
                rfm_data,
                x='RFM_Score_Num',
                title='RFM Score Distribution',
                labels={'RFM_Score_Num': 'RFM Score', 'count': 'Number of Customers'}
            )
            fig_rfm.update_layout(height=400)
            st.plotly_chart(fig_rfm, use_container_width=True)
        
        # Customer insights table
        st.subheader("📋 Customer Insights Summary")
        
        customer_insights = analytics.get_customer_insights()
        if customer_insights:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Average Customer Value",
                    f"${customer_insights['avg_customer_value']:,.2f}"
                )
            
            with col2:
                st.metric(
                    "Champions",
                    f"{customer_insights['champions_count']} customers"
                )
            
            with col3:
                st.metric(
                    "At Risk",
                    f"{customer_insights['at_risk_count']} customers"
                )
            
            # Recommendations
            st.markdown("### 💡 Customer Recommendations")
            for rec in customer_insights.get('recommendations', []):
                st.info(rec)

def display_product_performance(analytics):
    """Display product performance and ABC analysis"""
    st.subheader("📦 Product Performance & ABC Analysis")
    
    # Perform ABC analysis
    with st.spinner("Performing ABC analysis..."):
        product_abc, abc_stats = analytics.perform_abc_analysis()
    
    if product_abc is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Top products by revenue
            top_products = product_abc.head(10)
            fig_top_products = px.bar(
                top_products,
                x='Total_Revenue',
                y='Description',
                orientation='h',
                title='Top 10 Products by Revenue',
                labels={'Total_Revenue': 'Revenue ($)', 'Description': 'Product'}
            )
            fig_top_products.update_layout(height=500)
            st.plotly_chart(fig_top_products, use_container_width=True)
        
        with col2:
            # ABC category distribution
            abc_category_counts = product_abc['ABC_Category'].value_counts()
            fig_abc = px.pie(
                values=abc_category_counts.values,
                names=abc_category_counts.index,
                title='ABC Category Distribution',
                color_discrete_map={'A': '#ff7f0e', 'B': '#2ca02c', 'C': '#d62728'}
            )
            fig_abc.update_layout(height=400)
            st.plotly_chart(fig_abc, use_container_width=True)
        
        # ABC statistics
        st.subheader("📊 ABC Analysis Statistics")
        
        if abc_stats is not None:
            col1, col2, col3 = st.columns(3)
            
            for i, category in enumerate(['A', 'B', 'C']):
                cat_data = abc_stats[abc_stats['Category'] == category]
                if not cat_data.empty:
                    with [col1, col2, col3][i]:
                        st.metric(
                            f"Category {category}",
                            f"{cat_data['Product_Count'].iloc[0]} products",
                            f"{cat_data['Revenue_Percentage'].iloc[0]:.1f}% of revenue"
                        )

def display_forecasting(forecaster):
    """Display revenue forecasting"""
    st.subheader("📈 Revenue Forecasting")
    
    # Prepare time series data
    with st.spinner("Preparing forecasting data..."):
        monthly_data = forecaster.prepare_time_series_data()
    
    if monthly_data is not None:
        # Forecast periods selector
        forecast_periods = st.slider("Select forecast periods", 3, 12, 6)
        
        # Generate forecast
        with st.spinner("Generating forecast..."):
            forecast_report = forecaster.generate_forecast_report(periods=forecast_periods)
        
        if forecast_report:
            # Display forecast visualization
            st.plotly_chart(forecast_report['visualization'], use_container_width=True)
            
            # Forecast summary
            summary = forecast_report['summary']
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric(
                    "Total Forecasted Revenue",
                    f"${summary['total_forecasted_revenue']:,.0f}"
                )
            
            with col2:
                st.metric(
                    "Growth Rate",
                    f"{summary['forecast_growth_rate']:.1f}%"
                )
            
            with col3:
                st.metric(
                    "Avg Monthly Forecast",
                    f"${summary['avg_monthly_forecast']:,.0f}"
                )
            
            # Forecast recommendations
            st.markdown("### 💡 Forecast Recommendations")
            for rec in forecast_report.get('recommendations', []):
                if rec['type'] == 'Positive':
                    st.success(f"✅ {rec['message']}")
                elif rec['type'] == 'Warning':
                    st.warning(f"⚠️ {rec['message']}")
                else:
                    st.info(f"ℹ️ {rec['message']}")

def display_geographic_analysis(analytics):
    """Display geographic analysis"""
    st.subheader("🌍 Geographic Analysis")
    
    # Get geographic analysis
    geographic_data = analytics.get_geographic_analysis()
    
    if geographic_data is not None:
        col1, col2 = st.columns(2)
        
        with col1:
            # Revenue by country
            fig_country = px.bar(
                geographic_data.head(10),
                x='Total_Revenue',
                y='Country',
                orientation='h',
                title='Top 10 Countries by Revenue',
                labels={'Total_Revenue': 'Revenue ($)', 'Country': 'Country'}
            )
            fig_country.update_layout(height=500)
            st.plotly_chart(fig_country, use_container_width=True)
        
        with col2:
            # Customers by country
            fig_customers = px.bar(
                geographic_data.head(10),
                x='Customers',
                y='Country',
                orientation='h',
                title='Top 10 Countries by Customer Count',
                labels={'Customers': 'Number of Customers', 'Country': 'Country'}
            )
            fig_customers.update_layout(height=500)
            st.plotly_chart(fig_customers, use_container_width=True)
        
        # Geographic insights table
        st.subheader("📊 Geographic Insights")
        
        # Display top countries table
        st.dataframe(
            geographic_data.head(10)[['Country', 'Total_Revenue', 'Customers', 'Orders', 'Avg_Order_Value']]
            .round(2),
            use_container_width=True
        )

if __name__ == "__main__":
    main() 