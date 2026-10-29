import pdfplumber
import re

cleaned_rows = []

with pdfplumber.open("/Users/akashraj/Desktop/AgenticAI/test_log_analyzer/Tosca_Automation_Test_Report_10Pages.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for table in tables:
            for row in table:
                # Clean internal line breaks inside each cell
                clean_row = [re.sub(r'\s+', ' ', cell).strip() if cell else "" for cell in row]
                
                # Safeguard 1: Skip rows that don't have at least 4 columns (prevents IndexError)
                if len(clean_row) < 4:
                    continue
                
                # Safeguard 2: Skip repeating header rows or empty ID fields
                if not clean_row[0] or clean_row[0].upper() == "TEST CASE ID":
                    continue
                
                # Format as self-contained key-value record for the LLM
                record = (
                    f"Test Case ID: {clean_row[0]} | "
                    f"Test Case Name: {clean_row[1]} | "
                    f"Status: {clean_row[2]} | "
                    f"Execution Log: {clean_row[3]}"
                )
                cleaned_rows.append(record)

print(f"Successfully extracted {len(cleaned_rows)} test case rows!")

import json

# Saves as a clean JSON file on your Desktop
output_path = "/Users/akashraj/Desktop/AgenticAI/test_log_analyzer/cleaned_test_cases.json"
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(cleaned_rows, f, indent=4, ensure_ascii=False)

print(f"Cleaned file saved successfully to: {output_path}")
