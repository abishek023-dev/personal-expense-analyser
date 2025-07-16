import json
import os
import requests
from dotenv import load_dotenv

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

CATEGORIES = ["Food", "Travel", "Rent", "Shopping", "Income", "Bills", "Entertainment", "Other"]

def categorize_transactions_with_ai(transactions):
    """Use AI to categorize all transactions together"""
    print(f"🤖 Sending {len(transactions)} transactions to AI for categorization...")
    
    # Prepare transactions for AI
    transactions_text = []
    for i, trans in enumerate(transactions):
        transactions_text.append(f"{i+1}. {trans['desc']} | Amount: {trans['amount']} | Type: {trans['type']}")
    
    prompt = f"""
Categorize each transaction into one of these categories: {', '.join(CATEGORIES)}

Return a JSON array where each object has:
- "index": transaction number (1-{len(transactions)})
- "category": chosen category

Transactions:
{chr(10).join(transactions_text)}

Return only the JSON array, no explanation.
"""
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }
    
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    
    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        ai_output = result['candidates'][0]['content']['parts'][0]['text']
        
        print("🧠 AI Categorization Response:")
        print(ai_output)
        
        # Parse AI response
        categorizations = parse_ai_categorization(ai_output, len(transactions))
        
        # Apply categorizations
        categorized = []
        for i, transaction in enumerate(transactions):
            category = categorizations.get(i+1, fallback_categorize(transaction))
            categorized.append({
                **transaction,
                "category": category,
                "verified": False
            })
        
        return categorized
        
    except Exception as e:
        print(f"⚠️ AI categorization failed: {e}")
        print("🔄 Using fallback categorization...")
        return fallback_categorize_all(transactions)

def parse_ai_categorization(ai_output, expected_count):
    """Parse AI categorization response"""
    import re
    
    try:
        # Extract JSON from response
        start_idx = ai_output.find("[")
        end_idx = ai_output.rfind("]") + 1
        if start_idx == -1 or end_idx == -1:
            raise ValueError("No JSON array found")
        
        json_str = ai_output[start_idx:end_idx]
        categorizations_list = json.loads(json_str)
        
        # Convert to dict for easy lookup
        categorizations = {}
        for item in categorizations_list:
            index = item.get('index')
            category = item.get('category')
            
            if index and category in CATEGORIES:
                categorizations[index] = category
        
        print(f"✅ Parsed {len(categorizations)}/{expected_count} categorizations")
        return categorizations
        
    except Exception as e:
        print(f"❌ Failed to parse AI categorization: {e}")
        return {}

def fallback_categorize(transaction):
    """Simple rule-based fallback categorization"""
    desc = transaction['desc'].lower()
    
    if any(word in desc for word in ['zomato', 'swiggy', 'food', 'restaurant', 'cafe', 'eatclub']):
        return "Food"
    elif any(word in desc for word in ['uber', 'taxi', 'fuel', 'travel']):
        return "Travel"
    elif any(word in desc for word in ['rent', 'rentomojo']):
        return "Rent"
    elif any(word in desc for word in ['amazon', 'flipkart', 'shop', 'lifestyle', 'envogue']):
        return "Shopping"
    elif any(word in desc for word in ['netflix', 'spotify', 'jio', 'recharge']):
        return "Entertainment"
    elif any(word in desc for word in ['bill', 'charges', 'sms']):
        return "Bills"
    elif transaction['type'] == 'Credit' and transaction['amount'] > 10000:
        return "Income"
    else:
        return "Other"

def fallback_categorize_all(transactions):
    """Apply fallback categorization to all transactions"""
    categorized = []
    for transaction in transactions:
        category = fallback_categorize(transaction)
        categorized.append({
            **transaction,
            "category": category,
            "verified": False
        })
    return categorized

def show_categorization_results(categorized_transactions):
    """Show AI categorization results in a summary format"""
    print("\n🧠 AI CATEGORIZATION RESULTS")
    print("=" * 70)
    
    # Group by category for better overview
    by_category = {}
    for trans in categorized_transactions:
        category = trans['category']
        if category not in by_category:
            by_category[category] = []
        by_category[category].append(trans)
    
    # Show summary by category
    for category, transactions in sorted(by_category.items()):
        total_amount = sum(t['amount'] for t in transactions)
        print(f"\n🏷️ {category}: {len(transactions)} transactions, ₹{total_amount:.2f}")
        print("-" * 50)
        
        # Show top transactions in each category
        sorted_trans = sorted(transactions, key=lambda x: x['amount'], reverse=True)
        for i, trans in enumerate(sorted_trans[:5]):  # Show top 5
            print(f"  {i+1}. ₹{trans['amount']:>8.2f} - {trans['desc'][:45]}...")
        
        if len(transactions) > 5:
            print(f"  ... and {len(transactions) - 5} more")

def auto_verify_obvious_transactions(categorized_transactions):
    """Auto-verify transactions with obvious categorizations"""
    obvious_keywords = {
        'Food': ['zomato', 'swiggy', 'zepto', 'eatclub', 'dominos', 'pizza', 'restaurant', 'cafe'],
        'Travel': ['uber', 'ola', 'taxi', 'fuel', 'petrol', 'diesel', 'metro'],
        'Entertainment': ['netflix', 'spotify', 'prime', 'hotstar', 'youtube', 'gaming'],
        'Bills': ['electricity', 'water', 'gas', 'internet', 'mobile', 'recharge', 'jio', 'airtel'],
        'Rent': ['rent', 'rentomojo', 'rental'],
        'Shopping': ['amazon', 'flipkart', 'myntra', 'lifestyle', 'shopping', 'envogue']
    }
    
    auto_verified = 0
    
    for transaction in categorized_transactions:
        desc_lower = transaction['desc'].lower()
        category = transaction['category']
        
        # Auto-verify obvious transactions
        if category != 'Other':
            if category in obvious_keywords:
                keywords = obvious_keywords[category]
                if any(keyword in desc_lower for keyword in keywords):
                    transaction['verified'] = True
                    auto_verified += 1
            # Auto-verify high-value credits as Income
            elif category == 'Income' and transaction['type'] == 'Credit' and transaction['amount'] > 10000:
                transaction['verified'] = True
                auto_verified += 1
    
    print(f"✅ Auto-verified {auto_verified} obvious transactions")
    return auto_verified

def review_ambiguous_transactions(categorized_transactions):
    """Review only ambiguous transactions (unverified ones)"""
    # Find transactions that need review (unverified ones)
    needs_review = []
    for i, trans in enumerate(categorized_transactions):
        if not trans['verified']:
            needs_review.append((i, trans))
    
    if not needs_review:
        print("\n✅ All transactions are verified! No review needed.")
        return 0
    
    print(f"\n🔍 REVIEWING {len(needs_review)} AMBIGUOUS TRANSACTIONS")
    print("=" * 60)
    print("Only reviewing transactions that need clarification...")
    
    corrections = 0
    
    for review_idx, (original_idx, transaction) in enumerate(needs_review):
        print(f"\n📝 [{review_idx+1}/{len(needs_review)}] {transaction['desc']}")
        print(f"    Amount: ₹{transaction['amount']} | Type: {transaction['type']}")
        print(f"    🤖 AI Category: {transaction['category']}")
        
        while True:
            choice = input("    ❓ Correct? (y/n/s to skip remaining): ").lower().strip()
            
            if choice == 'y':
                transaction['verified'] = True
                print("    ✅ Verified")
                break
            elif choice == 'n':
                print(f"\n    Available categories: {', '.join(CATEGORIES)}")
                new_category = input("    Enter correct category: ").strip()
                
                if new_category in CATEGORIES:
                    old_category = transaction['category']
                    transaction['category'] = new_category
                    transaction['verified'] = True
                    corrections += 1
                    print(f"    ✅ Changed: {old_category} → {new_category}")
                    break
                else:
                    print("    ❌ Invalid category. Please try again.")
            elif choice == 's':
                print("    ⏭️ Skipping remaining reviews...")
                return corrections
            else:
                print("    ❌ Please enter 'y', 'n', or 's'")
    
    print(f"\n✅ Review complete! Made {corrections} corrections.")
    return corrections

def review_categorizations(categorized_transactions):
    """Smart review process - auto-verify obvious, review ambiguous"""
    # Show AI results first
    show_categorization_results(categorized_transactions)
    
    # Auto-verify obvious transactions
    auto_verified = auto_verify_obvious_transactions(categorized_transactions)
    
    # Review only ambiguous transactions
    corrections = review_ambiguous_transactions(categorized_transactions)
    
    total_verified = sum(1 for t in categorized_transactions if t['verified'])
    print(f"\n📊 FINAL SUMMARY:")
    print(f"   • Auto-verified: {auto_verified}")
    print(f"   • Manual corrections: {corrections}")
    print(f"   • Total verified: {total_verified}/{len(categorized_transactions)}")
    
    return corrections

def generate_summary(categorized_transactions):
    """Generate categorization summary"""
    summary = {}
    verified_count = 0
    
    for transaction in categorized_transactions:
        category = transaction['category']
        amount = transaction['amount']
        
        if category not in summary:
            summary[category] = {'total': 0, 'count': 0, 'transactions': []}
        
        summary[category]['total'] += amount
        summary[category]['count'] += 1
        summary[category]['transactions'].append({
            'desc': transaction['desc'],
            'amount': amount,
            'verified': transaction['verified']
        })
        
        if transaction['verified']:
            verified_count += 1
    
    print("\n📊 CATEGORIZATION SUMMARY")
    print("=" * 50)
    
    for category, data in sorted(summary.items(), key=lambda x: x[1]['total'], reverse=True):
        print(f"\n🏷️  {category}: ₹{data['total']:.2f} ({data['count']} transactions)")
        
        # Show top 3 transactions in each category
        top_transactions = sorted(data['transactions'], key=lambda x: x['amount'], reverse=True)[:3]
        for trans in top_transactions:
            status = "✅" if trans['verified'] else "❓"
            print(f"   {status} ₹{trans['amount']:.2f} - {trans['desc'][:40]}...")
    
    print(f"\n📈 Verification Status: {verified_count}/{len(categorized_transactions)} transactions verified")
    
    return summary

def save_categorized_data(categorized_transactions, filename="categorized_transactions.json"):
    """Save categorized transactions to file"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(categorized_transactions, f, indent=2)
    print(f"💾 Saved categorized data to {filename}")

def main():
    # Load transactions
    try:
        with open("output.json", 'r') as f:
            transactions = json.load(f)
    except FileNotFoundError:
        print("❌ output.json not found. Run pdf_reader.py first.")
        return
    
    print(f"📄 Loaded {len(transactions)} transactions")
    
    # Categorize with AI
    print("\n🤖 Starting AI categorization...")
    categorized = categorize_transactions_with_ai(transactions)
    
    # Interactive review
    review_categorizations(categorized)
    
    # Generate summary
    generate_summary(categorized)
    
    # Save results
    save_categorized_data(categorized)

if __name__ == "__main__":
    main()