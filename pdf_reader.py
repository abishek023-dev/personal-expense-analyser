import PyPDF2

def read_pdf_with_password(pdf_path, password):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)

            if reader.is_encrypted:
                success = reader.decrypt(password)
                if not success:
                    print("❌ Wrong password!")
                    return
                else:
                    print("🔓 PDF decrypted successfully.")
            else:
                print("PDF is not password-protected.")

            for i, page in enumerate(reader.pages):
                text = page.extract_text()
                print(f"\n----- Page {i+1} -----\n{text.strip() if text else '[No extractable text]'}")

    except Exception as e:
        print(f"Error: {e}")

# ✅ Example usage
read_pdf_with_password("bank_st2.pdf", "NAIS1402")
