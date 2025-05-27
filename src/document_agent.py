from langchain_community.document_loaders import PyPDFLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import CharacterTextSplitter
from langchain_core.prompts import PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
import os

DOCS_DIR = "docs/"
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

def load_policy_vectorstore():
    all_docs = []
    for filename in os.listdir(DOCS_DIR):
        if filename.endswith(".pdf"):
            loader = PyPDFLoader(os.path.join(DOCS_DIR, filename))
            docs = loader.load()
            all_docs.extend(docs)

    splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    split_docs = splitter.split_documents(all_docs)
    vectorstore = FAISS.from_documents(split_docs, embeddings)
    return vectorstore

def ask_documents(question, vectorstore, llm):
    qa_prompt = PromptTemplate.from_template(
        """Use the following documents to answer the question:
{context}

Question: {question}
Answer:"""
    )
    chain = create_stuff_documents_chain(llm, qa_prompt)
    retriever = vectorstore.as_retriever()
    docs = retriever.invoke(question)
    return chain.invoke({"context": docs, "question": question})