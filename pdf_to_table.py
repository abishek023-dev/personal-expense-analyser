import PyPDF2
import csv
import re

def extract_lines_from_pdf(pdf_path, password):
    all_lines = []
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
                all_lines.extend(lines)
    return all_lines

def find_schema_line(lines):
    for i, line in enumerate(lines):
        lower = line.lower()
        if ("date" in lower and "amount" in lower) or \
           ("date" in lower and ("withdrawal" in lower or "deposit" in lower)) or \
           ("narration" in lower and "amount" in lower):
            return i, re.split(r'\s{2,}|\t+', line.strip())  # split on large spaces/tabs
    return -1, []

def extract_table_rows(lines, start_idx, num_cols):
    table = []
    for line in lines[start_idx+1:]:
        if line.strip() == "":
            continue
        parts = re.split(r'\s{2,}|\t+', line.strip())  # split on large space/tab
        if len(parts) >= num_cols - 1:  # tolerate 1 missing sometimes
            # Pad if needed
            while len(parts) < num_cols:
                parts.append("")
            table.append(parts[:num_cols])
        else:
            # possibly footer or broken line
            break
    return table

def process_statement(pdf_path, password, output_csv="parsed_statement.csv"):
    lines = extract_lines_from_pdf(pdf_path, password)
    schema_index, headers = find_schema_line(lines)

    if schema_index == -1:
        print("❌ Could not detect schema line (no 'Date' and 'Amount' found).")
        return

    print(f"✅ Detected schema: {headers}")
    data_rows = extract_table_rows(lines, schema_index, len(headers))

    # Save to CSV
    with open(output_csv, "w", newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data_rows)

    print(f"✅ Extracted {len(data_rows)} rows → saved to {output_csv}")

process_statement("bank_st1.pdf", "NAIS1402")