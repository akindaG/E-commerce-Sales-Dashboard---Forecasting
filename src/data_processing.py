"""
Data Processing Module for E-commerce Analytics
Handles data loading, cleaning, and feature engineering
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
import os
warnings.filterwarnings('ignore')

class EcommerceDataProcessor:
    def __init__(self, file_path='data/Online_Retail.xlsx'):
        """
        Initialize the data processor
        
        Args:
            file_path (str): Path to the Excel file containing the retail data
        """
        self.file_path = file_path
        self.df = None
        self.cleaned_df = None
        
        # Try sample data if main file doesn't exist
        if not os.path.exists(file_path):
            sample_path = 'data/sample_online_retail.xlsx'
            if os.path.exists(sample_path):
                self.file_path = sample_path
                print(f"[DATA] Using sample data: {sample_path}")
            else:
                print(f"[DATA] Data file not found: {file_path}")
                print("[TIP] Run 'python src/sample_data_generator.py' to generate sample data")
        
    def load_data(self):
        """Load the raw data from Excel file"""
        try:
            self.df = pd.read_excel(self.file_path)
            print(f"[OK] Data loaded successfully: {self.df.shape[0]} rows, {self.df.shape[1]} columns")
            return self.df
        except FileNotFoundError:
            print("[ERROR] Data file not found. Please download the UCI Online Retail Dataset and place it in the data/ folder.")
            print("Download from: https://archive.ics.uci.edu/ml/datasets/online+retail")
            return None
        except Exception as e:
            print(f"[ERROR] Error loading data: {e}")
            return None
    
    def clean_data(self):
        """Clean and prepare the data for analysis"""
        if self.df is None:
            print("[ERROR] No data loaded. Please load data first.")
            return None
            
        # Create a copy for cleaning
        df_clean = self.df.copy()
        
        # Remove rows without customer ID
        df_clean = df_clean.dropna(subset=['CustomerID'])
        
        # Remove returns/negative quantities
        df_clean = df_clean[df_clean['Quantity'] > 0]
        
        # Remove zero-price items
        df_clean = df_clean[df_clean['UnitPrice'] > 0]
        
        # Convert InvoiceDate to datetime
        df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
        
        # Calculate total price
        df_clean['TotalPrice'] = df_clean['Quantity'] * df_clean['UnitPrice']
        
        # Create additional time-based features
        df_clean['Year'] = df_clean['InvoiceDate'].dt.year
        df_clean['Month'] = df_clean['InvoiceDate'].dt.month
        df_clean['DayOfWeek'] = df_clean['InvoiceDate'].dt.dayofweek
        df_clean['Hour'] = df_clean['InvoiceDate'].dt.hour
        df_clean['Quarter'] = df_clean['InvoiceDate'].dt.quarter
        df_clean['WeekOfYear'] = df_clean['InvoiceDate'].dt.isocalendar().week
        
        # Create day names for better visualization
        day_names = {0: 'Monday', 1: 'Tuesday', 2: 'Wednesday', 3: 'Thursday', 
                    4: 'Friday', 5: 'Saturday', 6: 'Sunday'}
        df_clean['DayName'] = df_clean['DayOfWeek'].map(day_names)
        
        # Create month names
        month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April',
                      5: 'May', 6: 'June', 7: 'July', 8: 'August',
                      9: 'September', 10: 'October', 11: 'November', 12: 'December'}
        df_clean['MonthName'] = df_clean['Month'].map(month_names)
        
        # Remove outliers (very high quantities or prices)
        q1_quantity = df_clean['Quantity'].quantile(0.01)
        q3_quantity = df_clean['Quantity'].quantile(0.99)
        q1_price = df_clean['UnitPrice'].quantile(0.01)
        q3_price = df_clean['UnitPrice'].quantile(0.99)
        
        df_clean = df_clean[
            (df_clean['Quantity'] >= q1_quantity) & 
            (df_clean['Quantity'] <= q3_quantity) &
            (df_clean['UnitPrice'] >= q1_price) & 
            (df_clean['UnitPrice'] <= q3_price)
        ]
        
        self.cleaned_df = df_clean
        
        print(f"[OK] Data cleaned successfully: {self.cleaned_df.shape[0]} rows remaining")
        print(f"[INFO] Data range: {self.cleaned_df['InvoiceDate'].min()} to {self.cleaned_df['InvoiceDate'].max()}")
        
        return self.cleaned_df
    
    def calculate_kpis(self):
        """Calculate key business metrics"""
        if self.cleaned_df is None:
            print("[ERROR] No cleaned data available. Please clean data first.")
            return None
            
        kpis = {
            'total_revenue': self.cleaned_df['TotalPrice'].sum(),
            'total_orders': self.cleaned_df['InvoiceNo'].nunique(),
            'total_customers': self.cleaned_df['CustomerID'].nunique(),
            'total_products': self.cleaned_df['StockCode'].nunique(),
            'avg_order_value': self.cleaned_df.groupby('InvoiceNo')['TotalPrice'].sum().mean(),
            'avg_items_per_order': self.cleaned_df.groupby('InvoiceNo')['Quantity'].sum().mean(),
            'date_range_start': self.cleaned_df['InvoiceDate'].min(),
            'date_range_end': self.cleaned_df['InvoiceDate'].max()
        }
        
        # Calculate revenue growth
        monthly_revenue = self.cleaned_df.groupby(self.cleaned_df['InvoiceDate'].dt.to_period('M'))['TotalPrice'].sum()
        if len(monthly_revenue) > 1:
            first_month = monthly_revenue.iloc[0]
            last_month = monthly_revenue.iloc[-1]
            kpis['revenue_growth_pct'] = ((last_month - first_month) / first_month) * 100
        else:
            kpis['revenue_growth_pct'] = 0
            
        return kpis
    
    def get_monthly_metrics(self):
        """Get monthly aggregated metrics"""
        if self.cleaned_df is None:
            print("[ERROR] No cleaned data available. Please clean data first.")
            return None
            
        monthly_metrics = self.cleaned_df.groupby(self.cleaned_df['InvoiceDate'].dt.to_period('M')).agg({
            'TotalPrice': 'sum',
            'CustomerID': 'nunique',
            'InvoiceNo': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        monthly_metrics.columns = ['Month', 'Revenue', 'Unique_Customers', 'Orders', 'Quantity_Sold']
        monthly_metrics['Month'] = monthly_metrics['Month'].dt.to_timestamp()
        monthly_metrics['Avg_Order_Value'] = monthly_metrics['Revenue'] / monthly_metrics['Orders']
        
        return monthly_metrics
    
    def get_daily_metrics(self):
        """Get daily aggregated metrics"""
        if self.cleaned_df is None:
            print("[ERROR] No cleaned data available. Please clean data first.")
            return None
            
        daily_metrics = self.cleaned_df.groupby(self.cleaned_df['InvoiceDate'].dt.date).agg({
            'TotalPrice': 'sum',
            'CustomerID': 'nunique',
            'InvoiceNo': 'nunique',
            'Quantity': 'sum'
        }).reset_index()
        
        daily_metrics.columns = ['Date', 'Revenue', 'Unique_Customers', 'Orders', 'Quantity_Sold']
        daily_metrics['Date'] = pd.to_datetime(daily_metrics['Date'])
        daily_metrics['Avg_Order_Value'] = daily_metrics['Revenue'] / daily_metrics['Orders']
        
        return daily_metrics
    
    def get_customer_metrics(self):
        """Get customer-level aggregated metrics"""
        if self.cleaned_df is None:
            print("[ERROR] No cleaned data available. Please clean data first.")
            return None
            
        customer_metrics = self.cleaned_df.groupby('CustomerID').agg({
            'InvoiceNo': 'nunique',
            'TotalPrice': 'sum',
            'Quantity': 'sum',
            'InvoiceDate': ['min', 'max']
        }).reset_index()
        
        customer_metrics.columns = ['CustomerID', 'Order_Count', 'Total_Spent', 'Total_Quantity', 'First_Order', 'Last_Order']
        customer_metrics['Avg_Order_Value'] = customer_metrics['Total_Spent'] / customer_metrics['Order_Count']
        
        return customer_metrics
    
    def get_product_metrics(self):
        """Get product-level aggregated metrics"""
        if self.cleaned_df is None:
            print("[ERROR] No cleaned data available. Please clean data first.")
            return None
            
        product_metrics = self.cleaned_df.groupby(['StockCode', 'Description']).agg({
            'Quantity': 'sum',
            'TotalPrice': 'sum',
            'InvoiceNo': 'nunique',
            'CustomerID': 'nunique'
        }).reset_index()
        
        product_metrics.columns = ['StockCode', 'Description', 'Total_Quantity', 'Total_Revenue', 'Order_Count', 'Customer_Count']
        product_metrics['Avg_Price'] = product_metrics['Total_Revenue'] / product_metrics['Total_Quantity']
        product_metrics['Avg_Quantity_Per_Order'] = product_metrics['Total_Quantity'] / product_metrics['Order_Count']
        
        return product_metrics.sort_values('Total_Revenue', ascending=False)
    
    def save_processed_data(self, output_path='data/processed_data.pkl'):
        """Save processed data for later use"""
        if self.cleaned_df is None:
            print("[ERROR] No cleaned data available. Please clean data first.")
            return False
            
        try:
            self.cleaned_df.to_pickle(output_path)
            print(f"[OK] Processed data saved to {output_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving data: {e}")
            return False
    
    def load_processed_data(self, input_path='data/processed_data.pkl'):
        """Load previously processed data"""
        try:
            self.cleaned_df = pd.read_pickle(input_path)
            print(f"[OK] Processed data loaded from {input_path}")
            return self.cleaned_df
        except FileNotFoundError:
            print(f"[ERROR] Processed data file not found: {input_path}")
            return None
        except Exception as e:
            print(f"[ERROR] Error loading processed data: {e}")
            return None

def main():
    """Main function to demonstrate data processing"""
    processor = EcommerceDataProcessor()
    
    # Load data
    df = processor.load_data()
    if df is None:
        return
    
    # Clean data
    cleaned_df = processor.clean_data()
    if cleaned_df is None:
        return
    
    # Calculate KPIs
    kpis = processor.calculate_kpis()
    if kpis:
        print("\n[INFO] Key Performance Indicators:")
        print(f"Total Revenue: ${kpis['total_revenue']:,.2f}")
        print(f"Total Orders: {kpis['total_orders']:,}")
        print(f"Total Customers: {kpis['total_customers']:,}")
        print(f"Average Order Value: ${kpis['avg_order_value']:.2f}")
        print(f"Revenue Growth: {kpis['revenue_growth_pct']:.1f}%")
    
    # Save processed data
    processor.save_processed_data()
    
    print("\n[OK] Data processing completed successfully!")

if __name__ == "__main__":
    main() 