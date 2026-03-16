import os
import tempfile

import fitz
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = None

if not api_key:
    st.error("OPENAI_API_KEY not found in .env file or Streamlit secrets")
    st.stop()

client = OpenAI(api_key=api_key)

st.set_page_config(page_title="Experra", page_icon="📄")
st.title("Experra")
st.subheader("Turn academic research into clear, structured explanations.")
st.write(
    "Upload a PDF to get the paper's main problem, key idea, methods, results, limitations, and study flashcards."
)

def extract_text_from_pdf(uploaded_file) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    doc = fitz.open(temp_path)
    all_text = []

    for page in doc:
        text = page.get_text("text", sort=True)
        all_text.append(text)

    doc.close()
    os.remove(temp_path)

    return "\n".join(all_text)

def chunk_text(text: str, max_chars: int = 12000):
    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end])
        start = end
    return chunks

def summarize_chunk(chunk: str) -> str:
    prompt = f"""
You are helping a student understand a research paper.

Analyze this paper excerpt and extract:
1. Main problem or question
2. Key idea
3. Methods used
4. Main results
5. Limitations
6. Important technical terms

Be accurate. If something is unclear, say so.

Paper excerpt:
{chunk[:8000]}
"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"Error analyzing chunk: {str(e)}"


def build_final_summary(chunk_summaries):
    joined = "\n\n".join(chunk_summaries)

    prompt = f"""
Combine the following partial paper analyses into one final report.

Use these headings:
# Paper Overview
# Problem
# Key Idea
# Methods
# Results
# Limitations
# Important Terms
# 5 Quick Study Flashcards

Keep it clear and useful for a student.

Partial analyses:
{joined}
"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text
    except Exception as e:
        return f"Error building final summary: {str(e)}"
st.divider()

uploaded_file = st.file_uploader("Upload a PDF", type=["pdf"])

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")

    if st.button("Analyze Paper"):
        with st.spinner("Extracting text from PDF..."):
            text = extract_text_from_pdf(uploaded_file)

        if not text.strip():
            st.error("Could not extract text from this PDF.")
        else:
            st.info(f"Extracted approximately {len(text):,} characters.")

            with st.spinner("Breaking paper into chunks..."):
                chunks = chunk_text(text)

            st.write(f"Number of chunks: {len(chunks)}")

            chunk_summaries = []

            for i, chunk in enumerate(chunks, start=1):
                with st.spinner(f"Analyzing chunk {i}/{len(chunks)}..."):
                    chunk_summary = summarize_chunk(chunk)
                    chunk_summaries.append(chunk_summary)

            with st.spinner("Building final report..."):
                final_summary = build_final_summary(chunk_summaries)

            st.subheader("Final Analysis")
            st.markdown(final_summary)

            st.download_button(
                label="Download Analysis as TXT",
                data=final_summary,
                file_name="paper_analysis.txt",
                mime="text/plain"
            )