"""
Sample Data Generator for E-commerce Analytics
Creates realistic sample data for demonstration purposes
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

class SampleDataGenerator:
    def __init__(self):
        """Initialize the sample data generator"""
        self.products = [
            {'code': 'P001', 'description': 'Wireless Bluetooth Headphones', 'price': 89.99},
            {'code': 'P002', 'description': 'Smartphone Case - Premium', 'price': 24.99},
            {'code': 'P003', 'description': 'USB-C Charging Cable', 'price': 12.99},
            {'code': 'P004', 'description': 'Portable Power Bank 10000mAh', 'price': 49.99},
            {'code': 'P005', 'description': 'Wireless Mouse - Ergonomic', 'price': 34.99},
            {'code': 'P006', 'description': 'Laptop Stand - Adjustable', 'price': 29.99},
            {'code': 'P007', 'description': 'Bluetooth Speaker - Waterproof', 'price': 79.99},
            {'code': 'P008', 'description': 'Phone Screen Protector', 'price': 9.99},
            {'code': 'P009', 'description': 'Wireless Charging Pad', 'price': 39.99},
            {'code': 'P010', 'description': 'Gaming Keyboard - RGB', 'price': 129.99},
            {'code': 'P011', 'description': 'Webcam HD 1080p', 'price': 59.99},
            {'code': 'P012', 'description': 'Microphone - USB Condenser', 'price': 89.99},
            {'code': 'P013', 'description': 'Tablet Stand - Foldable', 'price': 19.99},
            {'code': 'P014', 'description': 'Cable Organizer Set', 'price': 14.99},
            {'code': 'P015', 'description': 'Desk Lamp - LED Touch', 'price': 44.99},
        ]
        
        self.countries = ['United Kingdom', 'Germany', 'France', 'Netherlands', 'Spain', 'Italy', 'Belgium', 'Switzerland', 'Austria', 'Portugal']
        
    def generate_sample_data(self, num_transactions=50000, start_date='2010-12-01', end_date='2011-12-31'):
        """
        Generate sample e-commerce transaction data
        
        Args:
            num_transactions (int): Number of transactions to generate
            start_date (str): Start date for transactions
            end_date (str): End date for transactions
        """
        print(f"Generating {num_transactions:,} sample transactions...")
        
        # Generate date range
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        # Generate random dates
        date_range = (end_dt - start_dt).days
        random_days = np.random.randint(0, date_range, num_transactions)
        dates = [start_dt + timedelta(days=int(days)) for days in random_days]
        
        # Add some seasonality (higher sales in November-December)
        seasonal_boost = []
        for date in dates:
            if date.month in [11, 12]:  # Holiday season
                boost = np.random.choice([1, 1, 1, 1.5, 2], p=[0.6, 0.2, 0.1, 0.08, 0.02])
            elif date.month in [1, 2]:  # Post-holiday slump
                boost = np.random.choice([0.5, 0.7, 1], p=[0.3, 0.5, 0.2])
            else:
                boost = np.random.choice([0.8, 1, 1.2], p=[0.3, 0.5, 0.2])
            seasonal_boost.append(boost)
        
        # Generate transactions
        data = []
        
        for i in range(num_transactions):
            # Select random product
            product = random.choice(self.products)
            
            # Generate quantity (with some bulk orders)
            if random.random() < 0.1:  # 10% chance of bulk order
                quantity = random.randint(10, 50)
            else:
                quantity = random.randint(1, 5)
            
            # Apply seasonal boost
            quantity = int(quantity * seasonal_boost[i])
            
            # Generate customer ID (some repeat customers)
            if random.random() < 0.7:  # 70% chance of repeat customer
                customer_id = random.randint(1000, 5000)
            else:
                customer_id = random.randint(5001, 8000)
            
            # Generate invoice number (some customers buy multiple items)
            if random.random() < 0.3:  # 30% chance of same invoice
                invoice_no = f"INV-{customer_id}-{random.randint(1, 10):03d}"
            else:
                invoice_no = f"INV-{random.randint(10000, 99999)}"
            
            # Generate transaction
            transaction = {
                'InvoiceNo': invoice_no,
                'StockCode': product['code'],
                'Description': product['description'],
                'Quantity': quantity,
                'InvoiceDate': dates[i],
                'UnitPrice': product['price'],
                'CustomerID': customer_id,
                'Country': random.choice(self.countries)
            }
            
            data.append(transaction)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Sort by date
        df = df.sort_values('InvoiceDate')
        
        print(f"[OK] Generated {len(df):,} transactions")
        print(f"[INFO] Date range: {df['InvoiceDate'].min()} to {df['InvoiceDate'].max()}")
        print(f"[INFO] Unique customers: {df['CustomerID'].nunique():,}")
        print(f"[INFO] Unique products: {df['StockCode'].nunique():,}")
        print(f"[INFO] Total revenue: ${(df['Quantity'] * df['UnitPrice']).sum():,.2f}")
        
        return df
    
    def save_sample_data(self, output_path='data/sample_online_retail.xlsx'):
        """Save sample data to Excel file"""
        df = self.generate_sample_data()
        
        try:
            df.to_excel(output_path, index=False)
            print(f"[OK] Sample data saved to {output_path}")
            return True
        except Exception as e:
            print(f"[ERROR] Error saving sample data: {e}")
            return False

def main():
    """Main function to generate sample data"""
    generator = SampleDataGenerator()
    
    # Generate and save sample data
    success = generator.save_sample_data()
    
    if success:
        print("\n[SUCCESS] Sample data generation completed!")
        print("[INFO] You can now run the dashboard with: streamlit run dashboards/streamlit_app.py")
        print("[TIP] The sample data includes realistic seasonal patterns and customer behavior")

if __name__ == "__main__":
    main() 