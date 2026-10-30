import pdfplumber
import re
import os

pdf_path = "/Users/akashraj/Desktop/AgenticAI/image_rag/visual_document_with_chart.pdf"
os.makedirs("extracted_pdf_images", exist_ok=True)

cleaned_text_blocks = []

with pdfplumber.open(pdf_path) as pdf:
    for page_num, page in enumerate(pdf.pages):
        print(f"--- Processing Page {page_num + 1} ---")
        
        # 1. Extract and clean text from the page
        text = page.extract_text()
        if text:
            # Clean unwanted whitespace or repeating line breaks
            cleaned_text = re.sub(r'\s+', ' ', text).strip()
            cleaned_text_blocks.append({
                "page": page_num + 1,
                "content": cleaned_text
            })
        
        # 2. Extract any embedded images (charts/screenshots) from the page
        for img_index, img in enumerate(page.images):
            # pdfplumber extracts image streams; we can save them
            print(f"Found embedded image {img_index + 1} on page {page_num + 1}")

print(f"\nSuccessfully cleaned text from {len(cleaned_text_blocks)} pages!")
