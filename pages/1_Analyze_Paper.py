import os
import tempfile

import fitz
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI

st.set_page_config(page_title="Analyze Paper | Experra", page_icon="📄", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

.hero {
    padding: 2.5rem 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #1e293b 0%, #312e81 100%);
    border: 1px solid #475569;
}

.hero h1 {
    font-size: 3rem;
    line-height: 1.05;
    margin-bottom: 1rem;
    color: white;
}

.hero p {
    font-size: 1.15rem;
    color: #e2e8f0;
}

.card {
    padding: 1.5rem;
    border-radius: 18px;
    border: 1px solid #334155;
    background: #1e293b;
    min-height: 160px;
}

.card h3 {
    color: white;
}

.card p {
    color: #cbd5e1;
}

.small {
    color: #cbd5e1;
}

div.stButton > button {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    font-weight: 600;
    font-size: 1rem;
    transition: 0.2s ease;
}

div.stButton > button:hover {
    background: linear-gradient(135deg, #1d4ed8 0%, #1e40af 100%);
    color: white;
}

section[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

load_dotenv()

MAX_FREE_PAPERS = 3

if "papers_used" not in st.session_state:
    st.session_state.papers_used = 0

if "paper_text" not in st.session_state:
    st.session_state.paper_text = ""

if "final_summary" not in st.session_state:
    st.session_state.final_summary = ""

if "qa_history" not in st.session_state:
    st.session_state.qa_history = []

if st.session_state.papers_used >= MAX_FREE_PAPERS and not st.session_state.final_summary:
    st.warning("You've used your 3 free paper analyses. Upgrade coming soon.")
    st.stop()

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

st.markdown("""
<div class="hero">
    <h1>Analyze a research paper.</h1>
    <p>
    Upload an academic PDF and Experra will turn it into a clear research breakdown,
    study guide, flashcards, limitations, key terms, and follow-up Q&A.
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

remaining = MAX_FREE_PAPERS - st.session_state.papers_used
st.info(f"Free analyses remaining: {remaining}")

st.write("")

left, right = st.columns([1.3, 1])

with left:
    st.markdown("""
    <div class="card">
        <h3>Upload your paper</h3>
        <p class="small">Use a text-based academic PDF for best results. Scanned PDFs may not extract correctly yet.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")

    uploaded_file = st.file_uploader(
        "Upload an academic PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

with right:
    st.markdown("""
    <div class="card">
        <h3>Your report includes</h3>
        <p>✓ Paper overview</p>
        <p>✓ Problem and key idea</p>
        <p>✓ Methods and results</p>
        <p>✓ Limitations</p>
        <p>✓ Important terms</p>
        <p>✓ Study flashcards</p>
        <p>✓ Follow-up Q&A</p>
    </div>
    """, unsafe_allow_html=True)


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


def chunk_text(text: str, max_chars: int = 40000):
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
    except Exception:
        return "Analysis temporarily unavailable. Please try again."


def build_final_summary(chunk_summaries):
    joined = "\n\n".join(chunk_summaries)

    prompt = f"""
Combine the following partial paper analyses into one final report.

Use these headings:

# Paper Overview 
# Research Question 
# Why This Matters 
# Key Contribution
# Methods Explained Simply
# Key Results
# Limitations
# Important Terms
# 3 Quiz Questions
# 5 Study Flashcards
# Explain Like I'm Five

Keep it clear and useful for a student. Don't make it overly fancy. Incorporate direct/simple explanations when needed to build up to understanding and using the right vocabulary.

Partial analyses:
{joined}
"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text
    except Exception:
        return "Error building final summary. Please try again."

def analyze_full_paper(text: str) -> str:
    prompt = f"""
You are Experra, a research tutor helping a student understand an academic paper.

Analyze this academic paper and produce:

# Paper Overview 
# Research Question 
# Why This Matters 
# Key Contribution
# Methods Explained Simply
# Key Results
# Limitations
# Important Terms
# 3 Quiz Questions
# 5 Study Flashcards
# Explain Like I'm Five

Keep it clear and useful for a student. Don't make it overly fancy. Incorporate direct/simple explanations when needed to build up to understanding and using the right vocabulary.

Paper:
{text[:100000]}
"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text
    except Exception:
        return "Analysis temporarily unavailable. Please try again."

def format_qa_history(qa_history):
    if not qa_history:
        return "No previous questions yet."

    formatted = []

    for item in qa_history[-6:]:
        formatted.append(f"Student asked: {item['question']}\nExperra answered: {item['answer']}")

    return "\n\n".join(formatted)


def answer_question_about_paper(question: str, paper_text: str, final_summary: str, qa_history) -> str:
    previous_questions = format_qa_history(qa_history)

    prompt = f"""
You are Experra, a research tutor helping a student understand an academic paper.

Use the paper summary, original extracted paper text, and previous Q&A context to answer the student's latest question.

Rules:
- Answer clearly and accurately.
- Be educational, not overly formal.
- If the question asks for simplification, explain it step by step.
- If the student refers to something from a previous question, use the Q&A history.
- If the answer is not available from the paper, say that clearly.
- Do not hallucinate details that are not supported by the paper.
- Use simple explanations first, then introduce technical vocabulary.

Paper summary:
{final_summary}

Previous Q&A:
{previous_questions}

Original paper text excerpt:
{paper_text[:30000]}

Latest student question:
{question}
"""
    try:
        response = client.responses.create(
            model="gpt-4.1-mini",
            input=prompt
        )
        return response.output_text
    except Exception:
        return "Couldn't answer that question right now. Please try again."


def button_status(text):
    button_placeholder.markdown(f"""
    <div style="
        width:100%;
        padding: 0.76rem 1rem;
        border-radius:12px;
        background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
        text-align:center;
        font-weight:600;
        font-size:1rem;
        color:white;
        box-sizing:border-box;
        margin-bottom: 1rem;
    ">
    {text}
    </div>
    """, unsafe_allow_html=True)


st.write("")
st.divider()

if uploaded_file is not None:
    st.success(f"Uploaded: {uploaded_file.name}")

    button_placeholder = st.empty()
    status_placeholder = st.empty()

    analyze_clicked = button_placeholder.button(
        "Analyze Paper",
        use_container_width=True
    )

    if analyze_clicked:
        button_status("Analyzing... 0%")
        status_placeholder.caption("Extracting text from PDF...")

        text = extract_text_from_pdf(uploaded_file)

        if not text.strip():
            button_status("Analysis Failed")
            st.error("Could not extract text from this PDF.")
        else:
            status_placeholder.caption(f"Extracted approximately {len(text):,} characters.")

            if len(text) <= 100000:
                button_status("Analyzing paper... 50%")
                status_placeholder.caption("Using fast analysis mode for this paper...")

                final_summary = analyze_full_paper(text)

            else:
                chunks = chunk_text(text)
                status_placeholder.caption(f"Large paper detected. Split into {len(chunks)} section(s).")

                chunk_summaries = []

                for i, chunk in enumerate(chunks, start=1):
                    percent = int((i / len(chunks)) * 80)

                    button_status(f"Analyzing... {percent}%")
                    status_placeholder.caption(f"Analyzing section {i}/{len(chunks)}...")

                    chunk_summary = summarize_chunk(chunk)
                    chunk_summaries.append(chunk_summary)

                button_status("Building final report... 90%")
                status_placeholder.caption("Building final study report...")

                final_summary = build_final_summary(chunk_summaries)

            button_status("Analysis Complete ✓")
            status_placeholder.empty()

            st.session_state.papers_used += 1
            st.session_state.paper_text = text
            st.session_state.final_summary = final_summary
            st.session_state.qa_history = []
            st.write("")
            st.markdown("""
            <div class="hero">
                <h1>Final Analysis</h1>
                <p>Your paper has been converted into a clear study-ready report.</p>
            </div>
            """, unsafe_allow_html=True)

            st.write("")
            st.markdown(final_summary)

            st.download_button(
                label="Download Analysis as TXT",
                data=final_summary,
                file_name="paper_analysis.txt",
                mime="text/plain",
                use_container_width=True
            )

if st.session_state.final_summary:
    st.write("")
    st.divider()

    st.markdown("""
    <div class="hero">
        <h1>Ask follow-up questions.</h1>
        <p>Ask Experra to explain confusing sections, methods, results, assumptions, terminology, or what to study next.</p>
    </div>
    """, unsafe_allow_html=True)

    st.write("")
    st.subheader("Try asking:")

    q1, q2 = st.columns(2)
    q3, q4 = st.columns(2)

    def ask_preset(question):
        with st.spinner("Answering your question..."):
            answer = answer_question_about_paper(
                question,
                st.session_state.paper_text,
                st.session_state.final_summary,
                st.session_state.qa_history
            )

        st.session_state.qa_history.append(
            {
                "question": question,
                "answer": answer
            }
        )

    with q1:
        if st.button("Explain the methods more simply", use_container_width=True):
            ask_preset("Explain the methods section more simply, step by step.")

    with q2:
        if st.button("What are the biggest weaknesses?", use_container_width=True):
            ask_preset("What are the biggest weaknesses or limitations of this paper?")

    with q3:
        if st.button("What background do I need?", use_container_width=True):
            ask_preset("What background knowledge do I need to understand this paper well?")

    with q4:
        if st.button("Summarize this for a presentation", use_container_width=True):
            ask_preset("Summarize this paper like I need to present it in class or at a journal club.")

    st.write("")

    question = st.text_input(
        "Ask a question about this paper",
        placeholder="Example: Explain the methods section more simply."
    )

    if st.button("Ask Experra", type="primary", use_container_width=True):
        if not question.strip():
            st.warning("Type a question first.")
        else:
            with st.spinner("Answering your question..."):
                answer = answer_question_about_paper(
                    question,
                    st.session_state.paper_text,
                    st.session_state.final_summary,
                    st.session_state.qa_history
                )

            st.session_state.qa_history.append(
                {
                    "question": question,
                    "answer": answer
                }
            )

    if st.session_state.qa_history:
        st.write("")

        for index, item in enumerate(reversed(st.session_state.qa_history), start=1):
            with st.expander(item["question"]):
                st.markdown(item["answer"])

    st.write("")
    st.divider()

    st.markdown("""
    <div class="card">
        <h3>Want unlimited analyses?</h3>
        <p class="small">
        Want unlimited analyses? Experra Beta is opening soon. DM/email me for early access.
        </p>
    </div>
    """, unsafe_allow_html=True)

if not st.session_state.final_summary:
    st.write("")
    st.caption("Upload a PDF to begin.")