from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_community.llms import Ollama
from langchain.chains.question_answering import load_qa_chain
from langchain.document_loaders import PyPDFLoader
from langchain.text_splitter import CharacterTextSplitter
import os

# Load local embedding model
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Load local LLM (via Ollama)
llm = Ollama(model="llama3")
chain = load_qa_chain(llm, chain_type="stuff")

DOCS_DIR = "docs/"

def load_policy_vectorstore():
    all_docs = []

    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCS_DIR, filename))
            docs = loader.load()
            all_docs.extend(docs)

    # Split text into chunks
    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(all_docs)

    # Generate vector embeddings and save to FAISS
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    return vectorstore

def ask_documents(question, vectorstore):
    retriever = vectorstore.as_retriever()
    docs = retriever.get_relevant_documents(question)

    # Run local QA chain
    response = chain.run(input_documents=docs, question=question)
    return response
