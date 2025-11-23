#!/usr/bin/env python3
"""
Create business insights charts from libraff.az book data
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Use non-interactive backend
import seaborn as sns
from pathlib import Path

# Set style for professional-looking charts
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 11
plt.rcParams['axes.labelsize'] = 12
plt.rcParams['axes.titlesize'] = 14
plt.rcParams['xtick.labelsize'] = 10
plt.rcParams['ytick.labelsize'] = 10

# Load data
print("Loading data...")
df = pd.read_csv('libraff_books.csv')
print(f"Loaded {len(df)} books")

# Create charts directory
Path('charts').mkdir(exist_ok=True)

# Data cleaning
df['price'] = pd.to_numeric(df['price'], errors='coerce')
df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce')

print(f"\nData Summary:")
print(f"Total books: {len(df)}")
print(f"Price range: {df['price'].min():.2f} - {df['price'].max():.2f} AZN")
print(f"Average price: {df['price'].mean():.2f} AZN")
print(f"Total stock: {df['quantity'].sum():,.0f} units")

# ============================================================================
# CHART 1: Price Distribution
# ============================================================================
print("\n[1/6] Creating price distribution chart...")
plt.figure(figsize=(12, 7))

# Create price bins
price_bins = [0, 5, 10, 15, 20, 25, 30, 50, 100, df['price'].max()]
price_labels = ['0-5', '5-10', '10-15', '15-20', '20-25', '25-30', '30-50', '50-100', '100+']
df['price_range'] = pd.cut(df['price'], bins=price_bins, labels=price_labels)

price_dist = df['price_range'].value_counts().sort_index()

bars = plt.bar(range(len(price_dist)), price_dist.values, color='#2E86AB', alpha=0.8, edgecolor='black')
plt.xlabel('Price Range (AZN)', fontweight='bold')
plt.ylabel('Number of Books', fontweight='bold')
plt.title('Book Price Distribution - Most Books Priced Under 15 AZN', fontweight='bold', pad=20)
plt.xticks(range(len(price_dist)), price_dist.index, rotation=45)

# Add value labels on bars
for i, bar in enumerate(bars):
    height = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2., height,
             f'{int(height):,}',
             ha='center', va='bottom', fontweight='bold')

plt.tight_layout()
plt.savefig('charts/1_price_distribution.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: charts/1_price_distribution.png")

# ============================================================================
# CHART 2: Top 15 Categories (Level 2)
# ============================================================================
print("[2/6] Creating category breakdown chart...")
plt.figure(figsize=(14, 8))

top_categories = df['item_category2'].value_counts().head(15)

bars = plt.barh(range(len(top_categories)), top_categories.values, color='#A23B72', alpha=0.8, edgecolor='black')
plt.ylabel('Category', fontweight='bold')
plt.xlabel('Number of Books', fontweight='bold')
plt.title('Top 15 Book Categories - Fiction & Self-Development Lead', fontweight='bold', pad=20)
plt.yticks(range(len(top_categories)), top_categories.index)

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2.,
             f' {int(width):,}',
             ha='left', va='center', fontweight='bold')

plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('charts/2_top_categories.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: charts/2_top_categories.png")

# ============================================================================
# CHART 3: Stock Availability Status
# ============================================================================
print("[3/6] Creating stock availability chart...")
plt.figure(figsize=(12, 7))

# Categorize stock levels
def stock_status(qty):
    if qty == 0:
        return 'Out of Stock'
    elif qty <= 10:
        return 'Low Stock (1-10)'
    elif qty <= 50:
        return 'Medium Stock (11-50)'
    elif qty <= 100:
        return 'Good Stock (51-100)'
    else:
        return 'High Stock (100+)'

df['stock_status'] = df['quantity'].apply(stock_status)
stock_dist = df['stock_status'].value_counts()

# Define order and colors
stock_order = ['High Stock (100+)', 'Good Stock (51-100)', 'Medium Stock (11-50)',
               'Low Stock (1-10)', 'Out of Stock']
colors = ['#118AB2', '#06D6A0', '#FCBF49', '#F77F00', '#E63946']

stock_dist = stock_dist.reindex([s for s in stock_order if s in stock_dist.index])

bars = plt.barh(range(len(stock_dist)), stock_dist.values, color=colors, alpha=0.8, edgecolor='black')
plt.ylabel('Stock Status', fontweight='bold')
plt.xlabel('Number of Books', fontweight='bold')
plt.title('Inventory Health - Stock Availability Distribution', fontweight='bold', pad=20)
plt.yticks(range(len(stock_dist)), stock_dist.index)

# Add value labels and percentages
total_books = stock_dist.sum()
for i, bar in enumerate(bars):
    width = bar.get_width()
    percentage = (width / total_books) * 100
    plt.text(width, bar.get_y() + bar.get_height()/2.,
             f' {int(width):,} ({percentage:.1f}%)',
             ha='left', va='center', fontweight='bold')

plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('charts/3_stock_availability.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: charts/3_stock_availability.png")

# ============================================================================
# CHART 4: Main Category Distribution (Level 1)
# ============================================================================
print("[4/6] Creating main category distribution...")
plt.figure(figsize=(12, 8))

main_categories = df['item_category1'].value_counts()

colors_cat = sns.color_palette("husl", len(main_categories))
wedges, texts, autotexts = plt.pie(main_categories.values, labels=main_categories.index,
                                     autopct=lambda pct: f'{pct:.1f}%\n({int(pct/100.*main_categories.sum()):,})',
                                     colors=colors_cat, startangle=45,
                                     textprops={'fontsize': 10, 'fontweight': 'bold'})

plt.title('Catalog Distribution by Main Category', fontweight='bold', pad=20, fontsize=14)
plt.tight_layout()
plt.savefig('charts/4_main_categories.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: charts/4_main_categories.png")

# ============================================================================
# CHART 5: Average Price by Category (Top 10)
# ============================================================================
print("[5/6] Creating average price by category chart...")
plt.figure(figsize=(12, 8))

avg_price_by_cat = df.groupby('item_category2')['price'].mean().sort_values(ascending=False).head(10)

bars = plt.barh(range(len(avg_price_by_cat)), avg_price_by_cat.values,
                color='#F18F01', alpha=0.8, edgecolor='black')
plt.ylabel('Category', fontweight='bold')
plt.xlabel('Average Price (AZN)', fontweight='bold')
plt.title('Top 10 Highest-Priced Categories - Premium Product Mix', fontweight='bold', pad=20)
plt.yticks(range(len(avg_price_by_cat)), avg_price_by_cat.index)

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2.,
             f' {width:.2f} AZN',
             ha='left', va='center', fontweight='bold')

plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('charts/5_avg_price_by_category.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: charts/5_avg_price_by_category.png")

# ============================================================================
# CHART 6: Total Inventory Value by Category (Top 10)
# ============================================================================
print("[6/6] Creating inventory value by category chart...")
plt.figure(figsize=(12, 8))

df['inventory_value'] = df['price'] * df['quantity']
inv_value_by_cat = df.groupby('item_category2')['inventory_value'].sum().sort_values(ascending=False).head(10)

bars = plt.barh(range(len(inv_value_by_cat)), inv_value_by_cat.values / 1000,  # Convert to thousands
                color='#06A77D', alpha=0.8, edgecolor='black')
plt.ylabel('Category', fontweight='bold')
plt.xlabel('Total Inventory Value (Thousands AZN)', fontweight='bold')
plt.title('Top 10 Categories by Inventory Value - Revenue Potential', fontweight='bold', pad=20)
plt.yticks(range(len(inv_value_by_cat)), inv_value_by_cat.index)

# Add value labels
for i, bar in enumerate(bars):
    width = bar.get_width()
    plt.text(width, bar.get_y() + bar.get_height()/2.,
             f' {width:.1f}K',
             ha='left', va='center', fontweight='bold')

plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('charts/6_inventory_value_by_category.png', dpi=300, bbox_inches='tight')
plt.close()
print("✓ Saved: charts/6_inventory_value_by_category.png")

# ============================================================================
# Generate insights summary
# ============================================================================
print("\n" + "="*60)
print("CHARTS GENERATED SUCCESSFULLY")
print("="*60)

insights = f"""
KEY INSIGHTS FROM DATA ANALYSIS:

1. PRICING STRATEGY:
   - Average book price: {df['price'].mean():.2f} AZN
   - Most books ({price_dist.iloc[0:3].sum():,}) priced under 15 AZN
   - Price range: {df['price'].min():.2f} - {df['price'].max():.2f} AZN

2. CATALOG COMPOSITION:
   - Total unique books: {len(df):,}
   - Top category: {top_categories.index[0]} ({top_categories.values[0]:,} books)
   - Main category split: {dict(main_categories.head(3))}

3. INVENTORY STATUS:
   - Total inventory units: {df['quantity'].sum():,.0f}
   - Out of stock items: {len(df[df['quantity'] == 0]):,} ({len(df[df['quantity'] == 0])/len(df)*100:.1f}%)
   - High stock items (100+): {len(df[df['quantity'] >= 100]):,}

4. BUSINESS VALUE:
   - Total catalog value: {df['inventory_value'].sum():,.2f} AZN
   - Highest value category: {inv_value_by_cat.index[0]} ({inv_value_by_cat.values[0]:,.2f} AZN)
   - Average inventory per book: {df['quantity'].mean():.0f} units
"""

print(insights)

# Save insights to file
with open('charts/insights.txt', 'w', encoding='utf-8') as f:
    f.write(insights)

print("\n✓ All charts saved to 'charts/' directory")
print("✓ Insights saved to 'charts/insights.txt'")
