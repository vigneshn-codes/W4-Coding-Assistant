import streamlit as st
import os
from dotenv import load_dotenv

# LangChain (latest imports - no deprecation)
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

# Load environment variables
load_dotenv()

# Streamlit UI Config
st.set_page_config(page_title="AI Coding Assistant", page_icon="💻")
st.title("💻 AI Coding Assistant (LangChain + OpenAI)")

# Get API Key
openai_api_key = os.getenv("OPENAI_API_KEY")

if not openai_api_key:
    st.error("❌ Please set OPENAI_API_KEY in .env file")
    st.stop()

# Initialize LLM (Latest LangChain way)
llm = ChatOpenAI(
    model="gpt-4o-mini",  # fast & cost-effective
    temperature=0
)

# Prompt Template
prompt = ChatPromptTemplate.from_messages([
    ("system", 
     "You are an expert software engineer. "
     "Help users write clean, efficient, and production-ready code. "
     "Explain code clearly and provide improvements."),
    
    ("human", "{input}")
])

# Output Parser
parser = StrOutputParser()

# Chain (Prompt → LLM → Output)
chain = prompt | llm | parser

# UI Input
user_input = st.text_area("Ask your coding question:")

if st.button("Generate"):
    if user_input.strip():
        with st.spinner("Thinking..."):
            try:
                response = chain.invoke({"input": user_input})
                st.success("✅ Response:")
                st.write(response)
            except Exception as e:
                st.error(f"Error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a question")