# -*- coding: utf-8 -*-
"""Cópia de chatbot_INTO02.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1z4GcCFRW2v46bxznC4T0B3K_2KgrU47R
"""

#!pip install langchain faiss-cpu sentence-transformers
#!pip install langchain-community
#!pip install streamlit
#!pip install pypdf

#!pip install huggingface_hub[hf_xet]

from langchain.document_loaders import PyPDFLoader

# Carregar o PDF using the raw URL
loader = PyPDFLoader("https://raw.githubusercontent.com/sebavassou/chatbot_fila_into/main/dados/Cartilha-Funcionamento-da-Lista-de-Espera-do-Into_web2.pdf")
documents = loader.load()

from langchain.text_splitter import CharacterTextSplitter

splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
docs = splitter.split_documents(documents)

from langchain.embeddings import SentenceTransformerEmbeddings
from langchain.vectorstores import FAISS

# Criar embeddings com SentenceTransformer
embeddings = SentenceTransformerEmbeddings(model_name="all-mpnet-base-v2")

# Indexar os documentos com FAISS
vector_store = FAISS.from_documents(docs, embeddings)

import os
os.environ["OPENAI_API_KEY"] = "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"



from langchain.chat_models import ChatOpenAI

llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0)

from langchain.chains import RetrievalQA

retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 3})

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=retriever,
    return_source_documents=True
)

query = "Quais cuidados tenho que tomar no antes da cirurgia?"
result = qa_chain({"query": query})

print("Resposta:", result["result"])
print("\nFontes:")
for doc in result["source_documents"]:
    print(doc.page_content[:10])  # Exibe os primeiros 10 caracteres da fonte

# Interface Streamlit
import streamlit as st # Import streamlit

st.title("Chatbot INTO - Lista de Espera")

if "history" not in st.session_state:
    st.session_state.history = []

user_input = st.text_input("Digite sua pergunta:")

if st.button("Enviar") and user_input:
    result = qa_chain({"query": user_input})
    resposta = result["result"]
    fontes = [doc.page_content[:100] for doc in result["source_documents"]]
    st.session_state.history.append({"pergunta": user_input, "resposta": resposta, "fontes": fontes})

# Exibe o histórico de perguntas e respostas
for chat in reversed(st.session_state.history):
    st.markdown(f"**Você:** {chat['pergunta']}")
    st.markdown(f"**Chatbot:** {chat['resposta']}")
    with st.expander("Fontes"):
        for fonte in chat["fontes"]:
            st.write(fonte)
