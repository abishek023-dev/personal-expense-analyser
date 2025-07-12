import PyPDF2
import re
import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.environ.get("HF_TOKEN")

client = OpenAI(
    base_url="https://router.huggingface.co/featherless-ai/v1",
    api_key=HF_TOKEN,
)

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
                if reader.decrypt(password) != 1:
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

# 🤖 Send to LLM
def get_transactions_from_ai(masked_lines):
    prompt = f"""
Extract bank transactions from the following lines and return them in JSON format.

Each item should have:
- desc
- type (Credit/Debit)
- amount

Only return valid JSON list, no explanation.

Text:
{'\n'.join(masked_lines[:30])}
"""

    try:
        completion = client.chat.completions.create(
            model="HuggingFaceH4/zephyr-7b-beta",
            messages=[{"role": "user", "content": prompt}],
        ) 
        print(completion.choices[0].message.content)
        response_text = completion.choices[0].message.content
        return response_text
    except Exception as e:
        print(f"❌ API error: {e}")
        return ""

# 🧪 Try extracting JSON
def extract_json(response_text):
    try:
        # ✅ Extract all JSON arrays from response
        json_arrays = re.findall(r'\[\s*{.*?}\s*\]', response_text, re.DOTALL)

        # ✅ Parse all arrays and combine into one list
        all_transactions = []
        for array_str in json_arrays:
            try:
                items = json.loads(array_str)
                all_transactions.extend(items)
            except Exception as e:
                print(f"⚠️ Skipping one block due to error: {e}")

        return all_transactions
    except Exception as e:
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

    print("🚀 Sending to Hugging Face router...")
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
    process_pdf_and_send("bank_st1.pdf", "NAIS1402")
