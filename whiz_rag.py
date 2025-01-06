#RAG app - upload your PDF and ask questions
import os
import tempfile
import streamlit as st
import openai
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.document_loaders import PyPDFLoader
from langchain.chains import ConversationalRetrievalChain
from langchain.llms import OpenAI
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set your OpenAI API key
openai.api_key = st.secrets["OPEN_AI_KEY"]

# Streamlit UI
st.title("WhizCoach - Whizlabs AI - RAG App")
uploaded_file = st.file_uploader("Upload a PDF", type="pdf")

if uploaded_file:
    with st.spinner("Processing the PDF..."):
        # Save uploaded file to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            temp_file_path = temp_file.name

        try:
            # Load PDF and split into pages
            loader = PyPDFLoader(temp_file_path)
            pages = loader.load()

            # Generate embeddings
            embeddings = OpenAIEmbeddings(openai_api_key=openai.api_key)

            # Create FAISS vector store
            vector_store = FAISS.from_documents(pages, embeddings)

            # Create Conversational Retrieval Chain
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 5})
            qa_chain = ConversationalRetrievalChain.from_llm(
                OpenAI(openai_api_key=openai.api_key), retriever
            )

            st.success("PDF processed. Start asking questions!")
            chat_history = []

            # Chat loop
            user_input = st.text_input("Ask a question:")
            if user_input:
                with st.spinner("Generating response..."):
                    response = qa_chain({"question": user_input, "chat_history": chat_history})
                    chat_history.append((user_input, response["answer"]))
                    st.write(f"**Q:** {user_input}")
                    st.write(f"**A:** {response['answer']}")

        except Exception as e:
            st.error(f"An error occurred: {e}")

        finally:
            # Cleanup temporary file
            if os.path.exists(temp_file_path):
                os.remove(temp_file_path)
