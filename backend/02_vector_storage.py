import pandas as pd
import os
from llama import (
    save_to_disk,
    load_from_disk,
    process_documents,
    query_vector_db,
)

# Configuration
BASE_DIR = "backend/"
DB_PATH = BASE_DIR + "chroma_db"
COLLECTION_NAME = "founders_collection"
CSV_FILE = BASE_DIR + "transcripts.csv"
DATA_DIR = BASE_DIR + "data"
TEST_PROMPT = "What advice would you give a startup founder?"


def load_csv_to_markdown(csv_file, output_dir):
    """Convert CSV data into markdown files for processing."""
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(csv_file)

    for idx, row in df.iterrows():
        transcript = row["Transcript"]
        filename = os.path.join(output_dir, f"document_{idx}.md")

        with open(filename, "w", encoding="utf-8") as f:
            f.write(transcript)

    print(f"Processed {len(df)} documents into markdown files.")


def main():
    # Step 1: Load CSV and convert to markdown
    load_csv_to_markdown(CSV_FILE, DATA_DIR)

    # Step 2: Process Documents
    documents = process_documents(DATA_DIR)

    # Step 3: Store in ChromaDB
    index = save_to_disk(DB_PATH, COLLECTION_NAME, documents)

    # Step 4: Load from ChromaDB
    index = load_from_disk(DB_PATH, COLLECTION_NAME)

    # Step 5: Test Query
    response = query_vector_db(index, TEST_PROMPT)
    print("Query Response:", response)


if __name__ == "__main__":
    main()
