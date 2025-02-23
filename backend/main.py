from fastapi import FastAPI, Body
import uvicorn
from llama import load_from_disk, query_vector_db
import re

# Load your DB and collection on startup
BASE_DIR = "backend/"
DB_PATH = BASE_DIR + "chroma_db"
COLLECTION_NAME = "founders_collection"
index = load_from_disk(DB_PATH, COLLECTION_NAME)

app = FastAPI()


def extract_text_from_xml(xml_string, tag_name):
    # Regex pattern to find text within the specified tag
    pattern = f"<{tag_name}>(.*?)</{tag_name}>"

    # Search for the pattern in the XML string
    match = re.search(pattern, xml_string, re.DOTALL)

    if match:
        # Return the text inside the tag, stripping leading/trailing whitespace
        return match.group(1).strip()
    else:
        return "Tag not found"


def format_response(data):
    # Return sources and model response as a dict
    sources = []
    for entry in data.source_nodes:
        sources.append(entry.node.text)
    analysis = extract_text_from_xml(data.response, "context_analysis")
    response = extract_text_from_xml(data.response, "response")
    if response == "Tag not found":
        start_idx = data.response.find("<response>")
        if start_idx != -1:
            response = data.response[start_idx + len("<response>") :]
        else:
            response = "Tag not found"
    return {
        "sources": sources,
        "context_analysis": analysis,
        "response": response,
    }


@app.post("/query")
def get_response(query: str = Body(..., embed=True)):
    """
    Input: query (string)
    Output: JSON with sources and response
    """
    result = query_vector_db(index, query)
    return format_response(result)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
