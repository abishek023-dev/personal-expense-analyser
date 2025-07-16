import json
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os
import requests

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

def categorize_expenses(transactions):
    transactions_text = json.dumps(transactions[:20])
    prompt = f"""
Analyze these transactions and categorize each into: Food, Travel, Rent, Shopping, Income, Bills, Entertainment, Other.
Return only a JSON object with categories as keys and total amounts as values.

Transactions: {transactions_text}
"""
    
    headers = {
        "Content-Type": "application/json",
        "X-goog-api-key": GEMINI_API_KEY
    }

    data = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }

    try:
        response = requests.post(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent",
            headers=headers,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        model_output = result['candidates'][0]['content']['parts'][0]['text']
        
        # Extract JSON from response
        start_idx = model_output.find("{")
        end_idx = model_output.rfind("}") + 1
        if start_idx != -1 and end_idx != -1:
            json_str = model_output[start_idx:end_idx]
            return json.loads(json_str)
        else:
            raise Exception("No JSON found in response")
            
    except Exception as e:
        print(f"⚠️ Gemini API failed, using fallback: {e}")
        # Fallback categorization (keep existing fallback code)
        categories = {"Food": 0, "Travel": 0, "Shopping": 0, "Bills": 0, "Income": 0, "Other": 0}
        for t in transactions:
            desc = t.get('desc', '').lower()
            amount = float(t.get('amount', 0))
            
            if any(word in desc for word in ['food', 'restaurant', 'cafe']):
                categories["Food"] += amount
            elif any(word in desc for word in ['uber', 'taxi', 'fuel']):
                categories["Travel"] += amount
            elif any(word in desc for word in ['shop', 'amazon', 'flipkart']):
                categories["Shopping"] += amount
            elif t.get('type') == 'Credit':
                categories["Income"] += amount
            else:
                categories["Other"] += amount
        return categories

def create_dashboard(categories):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    
    # Pie chart
    labels = list(categories.keys())
    values = list(categories.values())
    ax1.pie(values, labels=labels, autopct='%1.1f%%')
    ax1.set_title('Expense Distribution')
    
    # Bar chart
    ax2.bar(labels, values)
    ax2.set_title('Amount by Category')
    ax2.tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig('expense_dashboard.png')
    plt.show()
    print("✅ Dashboard saved as expense_dashboard.png")

def analyze_expenses(json_file="output.json"):
    with open(json_file, 'r') as f:
        transactions = json.load(f)
    
    categories = categorize_expenses(transactions)
    create_dashboard(categories)
    
    print("\n📊 Expense Summary:")
    for category, amount in categories.items():
        print(f"{category}: ₹{amount:.2f}")

if __name__ == "__main__":
    analyze_expenses()