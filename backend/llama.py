import os
import json
import chromadb
import requests
import time
from llama_index.core import (
    VectorStoreIndex,
    StorageContext,
    SimpleDirectoryReader,
    get_response_synthesizer,
    Settings,
)
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.llms.anthropic import Anthropic
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import PromptTemplate
from dotenv import load_dotenv
import toml

load_dotenv()

Settings.embed_model = OpenAIEmbedding()
Settings.llm = Anthropic(
    model="claude-3-5-sonnet-latest", temperature=0, max_tokens=4096
)
Settings.chunk_size = 512
Settings.chunk_overlap = 128


def initialize_vector_db(db_path):
    """Initialize ChromaDB persistent client."""
    return chromadb.PersistentClient(path=db_path)


def save_to_disk(db_path, company_name, documents):
    """Save indexed documents to ChromaDB."""
    print("---Storing Documents---")
    db = initialize_vector_db(db_path)
    chroma_collection = db.get_or_create_collection(company_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    index = VectorStoreIndex.from_documents(documents, storage_context=storage_context)
    print("---Stored Documents---")
    return index


def load_from_disk(db_path, company_name):
    """Load indexed documents from ChromaDB."""
    print("---Loading Embeddings and Documents---")
    db = initialize_vector_db(db_path)
    chroma_collection = db.get_collection(company_name)
    vector_store = ChromaVectorStore(chroma_collection=chroma_collection)
    index = VectorStoreIndex.from_vector_store(vector_store)
    print("---Loaded Embeddings and Documents---")
    return index


def process_documents(data_dir):
    """Load markdown files as documents."""
    print("---Processing Documents---")
    documents = SimpleDirectoryReader(data_dir).load_data()
    print("---Processed Documents---")
    return documents


def query_vector_db(index, query, response_mode=None, top_k=8):
    """Query the vector database."""
    if response_mode is None:
        # response_synthesizer = get_response_synthesizer(response_mode="refine")

        tmpl_str = toml.load("backend/conf.toml")["prompts"]["founders_system_prompt"]
        prompt = PromptTemplate(tmpl_str)

        query_engine = index.as_query_engine(
            similarity_top_k=top_k,
            text_qa_template=prompt,
            refine_template=prompt,
            # response_synthesizer=response_synthesizer,
        )
    else:
        response_synthesizer = get_response_synthesizer(response_mode=response_mode)
        query_engine = index.as_query_engine(response_synthesizer=response_synthesizer)

    response = query_engine.query(query)
    print(response, flush=True)
    return response


def gpt_query(prompt, model="claude-3-sonnet-20240229", max_tokens=1024):
    """Query Anthropic Claude API."""
    client = Anthropic(model=model, temperature=0, max_tokens=max_tokens)
    message = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0,
        messages=[{"role": "user", "content": [{"type": "text", "text": prompt}]}],
    )
    return message.content[0].text


def delete_collection(db_path, collection_name):
    """Delete a collection from ChromaDB."""
    db = initialize_vector_db(db_path)
    db.delete_collection(collection_name)
