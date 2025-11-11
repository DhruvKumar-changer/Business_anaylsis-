

import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend for server deployment
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
import base64
from io import BytesIO

class ChartGenerator:
    """
    Chart Generator for creating business analytics visualizations
    
    All charts are returned as base64 strings for easy frontend integration
    """
    
    def __init__(self, style='whitegrid'):
        """
        Initialize chart generator with styling
        
        Args:
            style (str): Seaborn style ('whitegrid', 'darkgrid', 'white', 'dark')
        """
        sns.set_style(style)
        plt.rcParams['figure.figsize'] = (12, 6)
        plt.rcParams['font.size'] = 10
        
        # Color palette
        self.colors = sns.color_palette("husl", 8)
        
        print("✅ ChartGenerator initialized")
    
    def _plot_to_base64(self, fig):
        """
        Convert matplotlib figure to base64 string
        
        Args:
            fig: Matplotlib figure object
            
        Returns:
            str: Base64 encoded image string
        """
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=100)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        plt.close(fig)
        return image_base64
    
    def revenue_trend_chart(self, df, date_col='Date', revenue_col='Revenue'):
        """
        Create revenue trend line chart over time
        
        Args:
            df (pd.DataFrame): DataFrame with date and revenue columns
            date_col (str): Name of date column
            revenue_col (str): Name of revenue column
            
        Returns:
            str: Base64 encoded chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Ensure date column is datetime
            df[date_col] = pd.to_datetime(df[date_col])
            
            # Sort by date
            df_sorted = df.sort_values(date_col)
            
            # Plot line chart
            ax.plot(df_sorted[date_col], df_sorted[revenue_col], 
                   marker='o', linewidth=2, markersize=6, color=self.colors[0])
            
            # Styling
            ax.set_title('Revenue Trend Over Time', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Date', fontsize=12)
            ax.set_ylabel('Revenue (₹)', fontsize=12)
            ax.grid(True, alpha=0.3)
            
            # Format y-axis as currency
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
            
            # Rotate x-axis labels
            plt.xticks(rotation=45, ha='right')
            
            plt.tight_layout()
            
            print("✅ Revenue trend chart created")
            return self._plot_to_base64(fig)
        
        except Exception as e:
            print(f"❌ Error creating revenue trend chart: {e}")
            return None
    
    def product_comparison_chart(self, product_data):
        """
        Create product-wise revenue comparison bar chart
        
        Args:
            product_data (dict): Dictionary with product names as keys and metrics as values
                                 Example: {'Product A': {'revenue': 50000}, 'Product B': {'revenue': 30000}}
            
        Returns:
            str: Base64 encoded chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Extract data
            products = list(product_data.keys())
            revenues = [product_data[p].get('revenue', 0) for p in products]
            
            # Create bar chart
            bars = ax.bar(products, revenues, color=self.colors[:len(products)], 
                         edgecolor='black', linewidth=1.5)
            
            # Add value labels on top of bars
            for bar in bars:
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'₹{height:,.0f}',
                       ha='center', va='bottom', fontsize=10, fontweight='bold')
            
            # Styling
            ax.set_title('Product-wise Revenue Comparison', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Product', fontsize=12)
            ax.set_ylabel('Revenue (₹)', fontsize=12)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
            
            plt.xticks(rotation=45, ha='right')
            plt.tight_layout()
            
            print("✅ Product comparison chart created")
            return self._plot_to_base64(fig)
        
        except Exception as e:
            print(f"❌ Error creating product comparison chart: {e}")
            return None
    
    def expense_breakdown_chart(self, expense_data):
        """
        Create expense breakdown pie chart
        
        Args:
            expense_data (dict): Dictionary with expense categories and amounts
                                Example: {'Salaries': 50000, 'Rent': 20000, 'Marketing': 15000}
            
        Returns:
            str: Base64 encoded chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Extract data
            categories = list(expense_data.keys())
            amounts = list(expense_data.values())
            
            # Create pie chart
            wedges, texts, autotexts = ax.pie(
                amounts, 
                labels=categories, 
                autopct='%1.1f%%',
                startangle=90,
                colors=self.colors[:len(categories)],
                explode=[0.05] * len(categories),  # Slightly separate slices
                shadow=True
            )
            
            # Style percentage text
            for autotext in autotexts:
                autotext.set_color('white')
                autotext.set_fontweight('bold')
                autotext.set_fontsize(10)
            
            # Style labels
            for text in texts:
                text.set_fontsize(11)
                text.set_fontweight('bold')
            
            ax.set_title('Expense Breakdown', fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            print("✅ Expense breakdown chart created")
            return self._plot_to_base64(fig)
        
        except Exception as e:
            print(f"❌ Error creating expense breakdown chart: {e}")
            return None
        
    def forecast_chart(self, historical_data, predictions, labels=None):
        try:
            print(f"📊 Forecast chart - Historical: {len(historical_data)}, Predictions: {len(predictions) if predictions else 0}")
            
            fig, ax = plt.subplots(figsize=(14, 7))
            
            # Convert to lists
            historical_data = list(historical_data) if not isinstance(historical_data, list) else historical_data
            
            if predictions:
                predictions = list(predictions) if not isinstance(predictions, list) else predictions
            else:
                predictions = []
                print("⚠️ No predictions provided, showing only historical data")
            
            if len(historical_data) == 0:
                print("⚠️ No historical data")
                return None
            
            # Historical data
            hist_x = list(range(len(historical_data)))
            ax.plot(hist_x, historical_data, 
                marker='o', linewidth=2, markersize=8, 
                color=self.colors[0], label='Historical Data')
            
            # Predictions (only if available)
            if len(predictions) > 0:
                pred_x = list(range(len(historical_data), len(historical_data) + len(predictions)))
                ax.plot(pred_x, predictions, 
                    marker='s', linewidth=2, markersize=8, linestyle='--',
                    color=self.colors[1], label='Forecast')
                
                # Connection line
                ax.plot([hist_x[-1], pred_x[0]], 
                    [historical_data[-1], predictions[0]], 
                    linestyle=':', color='gray', linewidth=1.5)
                
                # Shaded forecast area
                ax.axvspan(len(historical_data)-0.5, len(historical_data)+len(predictions), 
                        alpha=0.1, color=self.colors[1])
                
                # Vertical separator line
                ax.axvline(x=len(historical_data)-0.5, color='red', 
                        linestyle='--', linewidth=2, alpha=0.5)
            
            # Styling
            ax.set_title('Sales Forecast', fontsize=16, fontweight='bold', pad=20)
            ax.set_xlabel('Time Period', fontsize=12)
            ax.set_ylabel('Revenue (₹)', fontsize=12)
            ax.legend(loc='upper left', fontsize=11)
            ax.grid(True, alpha=0.3)
            ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'₹{x:,.0f}'))
            
            plt.tight_layout()
            
            print("✅ Forecast chart created")
            return self._plot_to_base64(fig)
        
        except Exception as e:
            print(f"❌ Error creating forecast chart: {e}")
            import traceback
            traceback.print_exc()
            return None
        
    def kpi_dashboard_chart(self, kpis):
        """
        Create KPI summary dashboard
        
        Args:
            kpis (dict): Dictionary of KPI names and values
                        Example: {'Total Revenue': 500000, 'Profit Margin': 25.5, 'Customers': 1200}
            
        Returns:
            str: Base64 encoded chart image
        """
        try:
            fig, axes = plt.subplots(2, 2, figsize=(14, 10))
            fig.suptitle('Key Performance Indicators Dashboard', 
                        fontsize=18, fontweight='bold', y=0.98)
            
            kpi_items = list(kpis.items())
            
            for idx, (kpi_name, kpi_value) in enumerate(kpi_items[:4]):
                row = idx // 2
                col = idx % 2
                ax = axes[row, col]
                
                # Create a simple visualization for each KPI
                ax.text(0.5, 0.5, f'{kpi_value:,.2f}', 
                       ha='center', va='center', fontsize=36, fontweight='bold',
                       color=self.colors[idx])
                
                ax.text(0.5, 0.2, kpi_name,
                       ha='center', va='center', fontsize=14, fontweight='bold')
                
                ax.set_xlim(0, 1)
                ax.set_ylim(0, 1)
                ax.axis('off')
                
                # Add a colored rectangle border
                rect = plt.Rectangle((0.05, 0.05), 0.9, 0.9, 
                                    fill=False, edgecolor=self.colors[idx], 
                                    linewidth=3)
                ax.add_patch(rect)
            
            plt.tight_layout()
            
            print("✅ KPI dashboard chart created")
            return self._plot_to_base64(fig)
        
        except Exception as e:
            print(f"❌ Error creating KPI dashboard: {e}")
            return None
    
    def correlation_heatmap(self, df, columns=None):
        """
        Create correlation heatmap for numeric columns
        
        Args:
            df (pd.DataFrame): DataFrame with numeric columns
            columns (list): Specific columns to include (optional)
            
        Returns:
            str: Base64 encoded chart image
        """
        try:
            fig, ax = plt.subplots(figsize=(12, 10))
            
            # Select numeric columns
            if columns:
                data = df[columns]
            else:
                data = df.select_dtypes(include=[np.number])
            
            # Calculate correlation matrix
            corr_matrix = data.corr()
            
            # Create heatmap
            sns.heatmap(corr_matrix, annot=True, fmt='.2f', 
                       cmap='coolwarm', center=0,
                       square=True, linewidths=1, 
                       cbar_kws={"shrink": 0.8},
                       ax=ax)
            
            ax.set_title('Feature Correlation Heatmap', fontsize=16, fontweight='bold', pad=20)
            
            plt.tight_layout()
            
            print("✅ Correlation heatmap created")
            return self._plot_to_base64(fig)
        
        except Exception as e:
            print(f"❌ Error creating correlation heatmap: {e}")
            return None


# ========== EXAMPLE USAGE ==========
if __name__ == "__main__":
    print("=" * 60)
    print("CHART GENERATOR EXAMPLE")
    print("=" * 60)
    
    # Initialize generator
    generator = ChartGenerator()
    
    # 1. Revenue Trend Chart
    print("\n📊 Generating Revenue Trend Chart...")
    dates = pd.date_range(start='2024-01-01', periods=12, freq='M')
    revenue_df = pd.DataFrame({
        'Date': dates,
        'Revenue': [45000, 52000, 48000, 61000, 58000, 67000, 
                   72000, 69000, 75000, 80000, 78000, 85000]
    })
    revenue_chart = generator.revenue_trend_chart(revenue_df)
    print(f"Base64 length: {len(revenue_chart) if revenue_chart else 0}")
    
    # 2. Product Comparison Chart
    print("\n📊 Generating Product Comparison Chart...")
    product_data = {
        'Product A': {'revenue': 150000},
        'Product B': {'revenue': 120000},
        'Product C': {'revenue': 90000},
        'Product D': {'revenue': 75000}
    }
    product_chart = generator.product_comparison_chart(product_data)
    
    # 3. Expense Breakdown Chart
    print("\n📊 Generating Expense Breakdown Chart...")
    expense_data = {
        'Salaries': 80000,
        'Rent': 30000,
        'Marketing': 25000,
        'Utilities': 15000,
        'Misc': 10000
    }
    expense_chart = generator.expense_breakdown_chart(expense_data)
    
    # 4. Forecast Chart
    print("\n📊 Generating Forecast Chart...")
    historical = [45000, 52000, 48000, 61000, 58000, 67000]
    predictions = [70000, 72000, 75000, 78000, 80000, 82000]
    forecast_chart = generator.forecast_chart(historical, predictions)
    
    # 5. KPI Dashboard
    print("\n📊 Generating KPI Dashboard...")
    kpis = {
        'Total Revenue': 850000,
        'Profit Margin': 28.5,
        'Total Customers': 1250,
        'Avg Order Value': 680
    }
    kpi_chart = generator.kpi_dashboard_chart(kpis)
    
    print("\n" + "=" * 60)
    print("✅ All Charts Generated Successfully!")
    print("=" * 60)
    print("\n💡 Charts are base64 encoded strings")
    print("   Use in HTML: <img src='data:image/png;base64,{chart_data}'>")