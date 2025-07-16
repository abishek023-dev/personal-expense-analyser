import json
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime

def load_categorized_data(filename="categorized_transactions.json"):
    """Load categorized transaction data"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ {filename} not found. Run transaction_categorizer.py first.")
        return []

def create_enhanced_dashboard(categorized_transactions):
    """Create comprehensive dashboard with categorized data"""
    if not categorized_transactions:
        return
    
    # Prepare data
    categories = {}
    verified_categories = {}
    
    for trans in categorized_transactions:
        category = trans['category']
        amount = trans['amount']
        verified = trans['verified']
        
        if category not in categories:
            categories[category] = 0
            verified_categories[category] = 0
        
        categories[category] += amount
        if verified:
            verified_categories[category] += amount
    
    # Create subplots
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # 1. Pie chart - Overall distribution
    labels = list(categories.keys())
    values = list(categories.values())
    colors = plt.cm.Set3(range(len(labels)))
    
    ax1.pie(values, labels=labels, autopct='%1.1f%%', colors=colors)
    ax1.set_title('💰 Expense Distribution by Category', fontsize=14, fontweight='bold')
    
    # 2. Bar chart - Amount by category
    ax2.bar(labels, values, color=colors)
    ax2.set_title('📊 Total Amount by Category', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Amount (₹)')
    ax2.tick_params(axis='x', rotation=45)
    
    # 3. Verification status
    verified_values = list(verified_categories.values())
    unverified_values = [categories[cat] - verified_categories[cat] for cat in labels]
    
    x_pos = range(len(labels))
    ax3.bar(x_pos, verified_values, label='Verified', color='lightgreen', alpha=0.8)
    ax3.bar(x_pos, unverified_values, bottom=verified_values, label='Unverified', color='lightcoral', alpha=0.8)
    ax3.set_title('✅ Verification Status by Category', fontsize=14, fontweight='bold')
    ax3.set_ylabel('Amount (₹)')
    ax3.set_xticks(x_pos)
    ax3.set_xticklabels(labels, rotation=45)
    ax3.legend()
    
    # 4. Transaction count by category
    category_counts = {}
    for trans in categorized_transactions:
        category = trans['category']
        category_counts[category] = category_counts.get(category, 0) + 1
    
    ax4.bar(category_counts.keys(), category_counts.values(), color=colors)
    ax4.set_title('📈 Transaction Count by Category', fontsize=14, fontweight='bold')
    ax4.set_ylabel('Number of Transactions')
    ax4.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('enhanced_expense_dashboard.png', dpi=300, bbox_inches='tight')
    plt.show()
    print("✅ Enhanced dashboard saved as enhanced_expense_dashboard.png")

def generate_detailed_report(categorized_transactions):
    """Generate detailed expense report"""
    print("\n📋 DETAILED EXPENSE REPORT")
    print("=" * 60)
    
    total_amount = sum(trans['amount'] for trans in categorized_transactions)
    verified_count = sum(1 for trans in categorized_transactions if trans['verified'])
    
    print(f"📊 Total Transactions: {len(categorized_transactions)}")
    print(f"💰 Total Amount: ₹{total_amount:.2f}")
    print(f"✅ Verified: {verified_count}/{len(categorized_transactions)} ({verified_count/len(categorized_transactions)*100:.1f}%)")
    
    # Category breakdown
    categories = {}
    for trans in categorized_transactions:
        category = trans['category']
        if category not in categories:
            categories[category] = {'total': 0, 'count': 0, 'verified': 0, 'transactions': []}
        
        categories[category]['total'] += trans['amount']
        categories[category]['count'] += 1
        if trans['verified']:
            categories[category]['verified'] += 1
        categories[category]['transactions'].append(trans)
    
    print(f"\n🏷️  CATEGORY BREAKDOWN")
    print("-" * 40)
    
    for category, data in sorted(categories.items(), key=lambda x: x[1]['total'], reverse=True):
        percentage = (data['total'] / total_amount) * 100
        verification_rate = (data['verified'] / data['count']) * 100
        
        print(f"\n{category}:")
        print(f"  💰 Total: ₹{data['total']:.2f} ({percentage:.1f}%)")
        print(f"  📊 Count: {data['count']} transactions")
        print(f"  ✅ Verified: {verification_rate:.1f}%")
        
        # Show largest transactions in category
        top_trans = sorted(data['transactions'], key=lambda x: x['amount'], reverse=True)[:3]
        print(f"  🔝 Top transactions:")
        for i, trans in enumerate(top_trans, 1):
            status = "✅" if trans['verified'] else "❓"
            print(f"     {i}. {status} ₹{trans['amount']:.2f} - {trans['desc'][:35]}...")

def export_to_csv(categorized_transactions, filename="expense_report.csv"):
    """Export categorized data to CSV"""
    df = pd.DataFrame(categorized_transactions)
    df.to_csv(filename, index=False)
    print(f"📄 Exported to {filename}")

def find_miscategorized(categorized_transactions):
    """Find potentially miscategorized transactions"""
    print("\n🔍 POTENTIAL MISCATEGORIZATIONS")
    print("=" * 50)
    
    suspicious = []
    
    for trans in categorized_transactions:
        desc = trans['desc'].lower()
        category = trans['category']
        
        # Check for obvious mismatches
        if 'zomato' in desc or 'swiggy' in desc:
            if category != 'Food':
                suspicious.append((trans, 'Should be Food'))
        elif 'netflix' in desc or 'spotify' in desc:
            if category != 'Entertainment':
                suspicious.append((trans, 'Should be Entertainment'))
        elif 'rent' in desc:
            if category != 'Rent':
                suspicious.append((trans, 'Should be Rent'))
    
    if suspicious:
        print(f"Found {len(suspicious)} potentially miscategorized transactions:")
        for trans, suggestion in suspicious:
            status = "✅" if trans['verified'] else "❓"
            print(f"{status} ₹{trans['amount']:.2f} - {trans['desc'][:40]}...")
            print(f"   Current: {trans['category']} | {suggestion}")
    else:
        print("✅ No obvious miscategorizations found!")

def main():
    categorized_transactions = load_categorized_data()
    if not categorized_transactions:
        return
    
    print(f"📄 Loaded {len(categorized_transactions)} categorized transactions")
    
    # Create enhanced dashboard
    create_enhanced_dashboard(categorized_transactions)
    
    # Generate detailed report
    generate_detailed_report(categorized_transactions)
    
    # Find potential issues
    find_miscategorized(categorized_transactions)
    
    # Export to CSV
    export_to_csv(categorized_transactions)

if __name__ == "__main__":
    main()