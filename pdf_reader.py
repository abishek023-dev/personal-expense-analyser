import PyPDF2
import re
import os
import json
from dotenv import load_dotenv
import requests

load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")

# 🔐 Mask long digits (like account no, UPI IDs)
def mask_sensitive_digits(text):
    return re.sub(r'\d{4,}', lambda m: '*' * len(m.group()), text)

# 📄 Read and clean PDF
def extract_masked_text_from_pdf(pdf_path, password):
    all_lines = []
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            if reader.is_encrypted:
                if not reader.decrypt(password):
                    print("❌ Wrong password!")
                    return []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    lines = text.split('\n')
                    masked_lines = [mask_sensitive_digits(line.strip()) for line in lines if line.strip()]
                    all_lines.extend(masked_lines)

        print(f"✅ Read {len(all_lines)} lines from PDF.")
        return all_lines
    except Exception as e:
        print(f"❌ Error reading PDF: {e}")
        return []

# 🤖 Send to Gemini API
def get_transactions_from_ai(masked_lines):
    text_content = '\n'.join(masked_lines)
    prompt = f"""
Extract all bank transactions from the following lines and return only valid JSON list. 

Each item should include:
- desc
- type (Credit/Debit)
- amount

Only return the JSON array, without any explanation or formatting.

Text:
{text_content}
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
        print("🧠 Gemini Output:\n", model_output)
        return model_output
    except Exception as e:
        print(f"❌ API error: {e}")
        return ""

# 🧪 Try extracting JSON
def extract_json(response_text):
    try:
        start_idx = response_text.find("[")
        end_idx = response_text.rfind("]") + 1
        if start_idx == -1 or end_idx == -1:
            print("❌ No valid JSON block found.")
            return []

        json_block = response_text[start_idx:end_idx]

        # Fix bad backslashes
        json_block = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', json_block)

        transactions = json.loads(json_block)
        return transactions
    except json.JSONDecodeError as e:
        print(f"❌ JSON parsing failed: {e}")
        return []

# 💾 Save output
def save_to_json(data, filename="output.json"):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved {len(data)} transactions to {filename}")

# 🚀 Main logic
def process_pdf_and_send(pdf_path, password):
    print("🔍 Reading and masking PDF...")
    masked_lines = extract_masked_text_from_pdf(pdf_path, password)
    if not masked_lines:
        return

    print("🚀 Sending to Gemini API...")
    response = get_transactions_from_ai(masked_lines)
    if not response:
        return

    transactions = extract_json(response)
    if transactions:
        save_to_json(transactions)
    else:
        print("❌ Couldn’t parse any transaction.")

# ✅ Run
if __name__ == "__main__":
    process_pdf_and_send("bank_st2.pdf", "NAIS1402")
