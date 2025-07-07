import PyPDF2
import re
import pandas as pd

# 👉 Function to classify type (Credit/Debit)
def classify_type(desc):
    desc_lower = desc.lower()
    if any(word in desc_lower for word in ["credit", "salary", "cr", "received"]):
        return "Credit"
    return "Debit"

# 👉 Parse a transaction line
def parse_transaction_line(line):
    try:
        amt_match = re.search(r"₹?\s?([\d,]+\.\d{2})", line)
        if not amt_match:
            return None
        amount = float(amt_match.group(1).replace(",", ""))

        date_match = re.match(r"^\d{1,2}[-/]\d{1,2}[-/]\d{2,4}", line)
        if not date_match:
            return None
        date_end = date_match.end()

        desc = line[date_end:amt_match.start()].strip()
        txn_type = classify_type(desc)

        return {
            "desc": desc,
            "type": txn_type,
            "amount": amount
        }

    except:
        return None

# 🔓 Main PDF processing function
def process_pdf_transactions(pdf_path, password):
    results = []
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
                    for line in lines:
                        parsed = parse_transaction_line(line.strip())
                        if parsed:
                            results.append(parsed)
        return results

    except Exception as e:
        print(f"Error: {e}")
        return []

# ✅ Example usage
pdf_path = "bank_st2.pdf"
password = "NAIS1402"

parsed_data = process_pdf_transactions(pdf_path, password)

# Show result
for entry in parsed_data:
    print(entry)

# Optional: Save to CSV/JSON
pd.DataFrame(parsed_data).to_csv("transactions_no_category.csv", index=False)
