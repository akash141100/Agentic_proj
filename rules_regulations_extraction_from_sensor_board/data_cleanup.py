from unstructured.partition.pdf import partition_pdf
from unstructured.cleaners.core import clean_extra_whitespace, clean_non_ascii_chars
from unstructured.documents.elements import Header, Footer, PageNumber

def extract_and_clean_scanned_pdf(file_path: str):
    # 1. Parse the scanned document using vision models and OCR
    elements = partition_pdf(
        filename=file_path,
        strategy="hi_res",
        infer_table_structure=True,  # Set to True if the scan contains tables
        languages=["eng"]
    )

    cleaned_text_chunks = []

    # 2. Iterate through extracted elements and filter/clean them
    for element in elements:
        # Filter out unwanted layout noise
        if isinstance(element, (Header, Footer, PageNumber)):
            continue

        # Extract raw text from the element
        text = element.text
        
        # Apply Unstructured's built-in cleaning functions
        text = clean_non_ascii_chars(text)
        text = clean_extra_whitespace(text)

        # Ignore empty strings after cleaning
        if text:
            cleaned_text_chunks.append(text)

    return cleaned_text_chunks

# Execute the extraction
scanned_file = "/Users/akashraj/Desktop/AgenticAI/rules_regulations_extraction_from_sensor_board/cine_act1952.pdf"
clean_data = extract_and_clean_scanned_pdf(scanned_file)

# 3. Store the cleaned data (Example: saving to a file for ingestion)
with open("cine_act1952_cleaned.pdf", "w", encoding="utf-8") as f:
    f.write("\n\n".join(clean_data))
    
print(f"Successfully cleaned and stored {len(clean_data)} document elements.")
