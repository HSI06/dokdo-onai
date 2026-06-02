from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def load_rag():
    loader = TextLoader("docs\\dokdo_all.txt", encoding="utf-8")
    docs = loader.load()
    
    splitter = RecursiveCharacterTextSplitter(chunk_size=150, chunk_overlap=20)
    splits = splitter.split_documents(docs)
    
    embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
    
    vectorstore = Chroma.from_documents(splits, embeddings, persist_directory="chroma_db")
    return vectorstore.as_retriever(search_kwargs={"k": 5})

def search_docs(retriever, query):
    results = retriever.invoke(query)
    return "\n".join([doc.page_content for doc in results])