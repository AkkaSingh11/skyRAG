from pathlib import Path
from typing import List
from langchain_community.document_loaders import (
    PyPDFLoader, Docx2txtLoader, TextLoader, UnstructuredMarkdownLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document
import os

SOURCE_DIR = Path("docs")
INDEX_DIR = Path("chroma_db_gemini")
COLLECTION = "kb_collection_gemini"
EMBED_MODEL = "gemini-embedding-001"

def load_documents(folder_path: str) -> List[Document]:
    documents = []
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if filename.endswith('.pdf'):
            loader = PyPDFLoader(file_path)
        elif filename.endswith('.docx'):
            loader = Docx2txtLoader(file_path)
        else:
            print(f"Unsupported file type: {filename}")
            continue
        documents.extend(loader.load())
    return documents

def create_vector_store():
    if not os.path.exists(SOURCE_DIR):
        os.makedirs(SOURCE_DIR)
        print(f"Created '{SOURCE_DIR}' directory. Please add your documents to it.")
        return None

    documents = load_documents(str(SOURCE_DIR))
    if not documents:
        print("No documents found to index.")
        return None

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks = text_splitter.split_documents(documents)
    
    embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(INDEX_DIR),
        collection_name=COLLECTION,
    )
    vectordb.persist()
    print("Index built at", INDEX_DIR.resolve())
    return vectordb

def get_retriever():
    if not INDEX_DIR.exists():
        vectordb = create_vector_store()
    else:
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBED_MODEL)
        vectordb = Chroma(
            persist_directory=str(INDEX_DIR),
            embedding_function=embeddings,
            collection_name=COLLECTION
        )
    if vectordb:
        return vectordb.as_retriever(search_kwargs={"k": 2})
    return None
