import re
import pdfplumber
import pikepdf

def mask_sensitive_digits(text):
    return re.sub(r'\d{4,}', lambda m: '*' * len(m.group()), text)

def extract_masked_text_pikepdf(pdf_path, password=""):
    temp_file = "temp_unlocked.pdf"
    try:
        # 🛡️ Decrypt with pikepdf and save as a temp unlocked PDF
        with pikepdf.open(pdf_path, password=password) as pdf:
            pdf.save(temp_file)

        lines = []
        with pdfplumber.open(temp_file) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    for line in text.split('\n'):
                        line = line.strip()
                        if line:
                            lines.append(mask_sensitive_digits(line))

        print(f"✅ Extracted {len(lines)} lines.")
        return lines

    except Exception as e:
        print(f"❌ Failed to read PDF: {e}")
        return []

# ✅ Run
if __name__ == "__main__":
    result = extract_masked_text_pikepdf("bank_st2.pdf", "NAIS1402")
    for line in result[:10]:
        print(line)
