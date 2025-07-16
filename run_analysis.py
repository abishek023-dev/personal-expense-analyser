#!/usr/bin/env python3
"""
Complete Expense Analysis Workflow
"""

import os
import sys

def main():
    print("🏦 PERSONAL EXPENSE ANALYZER")
    print("=" * 40)
    
    # Check if output.json exists
    if not os.path.exists("output.json"):
        print("📄 No transaction data found. Run pdf_reader.py first.")
        return
    
    print("🤖 Starting transaction categorization...")
    result = os.system("python transaction_categorizer.py")
    if result != 0:
        print("❌ Error in categorization")
        return
    
    print("\n📊 Generating enhanced analysis...")
    result = os.system("python enhanced_analyzer.py")
    if result != 0:
        print("❌ Error in analysis")
        return
    
    print("\n🎉 Analysis complete!")
    print("📁 Check these files:")
    print("   • categorized_transactions.json")
    print("   • enhanced_expense_dashboard.png")
    print("   • expense_report.csv")

if __name__ == "__main__":
    main()