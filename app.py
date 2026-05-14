import streamlit as st

st.set_page_config(page_title="Experra", page_icon="📄", layout="wide")

st.markdown("""
<style>
.block-container {
    padding-top: 3rem;
    padding-bottom: 3rem;
    max-width: 1100px;
}

.hero {
    padding: 3rem 2rem;
    border-radius: 24px;
    background: linear-gradient(135deg, #1e293b 0%, #312e81 100%);
    border: 1px solid #475569;
}

.hero h1 {
    font-size: 3.5rem;
    line-height: 1.05;
    margin-bottom: 1rem;
    color: white;
}

.hero p {
    font-size: 1.25rem;
    color: #e2e8f0;
}

.card {
    padding: 1.5rem;
    border-radius: 18px;
    border: 1px solid #334155;
    background: #1e293b;
    min-height: 200px;
    display: flex;
    flex-direction: column;
    justify-content: flex-start;
}

.card h3 {
    color: white;
}

.card p {
    color: #cbd5e1;
}

.price {
    font-size: 2rem;
    font-weight: 700;
    color: white;
}

.small {
    color: #cbd5e1;
}
section[data-testid="stSidebar"] {
    display: none;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="hero">
    <h1>Understand research papers in minutes.</h1>
    <p>
    Experra turns dense academic PDFs into clear explanations, study guides,
    flashcards, and key insights instantly.
    </p>
</div>
""", unsafe_allow_html=True)

st.write("")

if st.button("Try Experra Free", type="primary", use_container_width=True):
    st.switch_page("pages/1_Analyze_Paper.py")

st.write("")
st.write("")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("""
    <div class="card">
        <h3>Clear summaries</h3>
        <p class="small">Get the main problem, thesis, contribution, and results without decoding academic jargon.</p>
    </div>
    """, unsafe_allow_html=True)

with col2:
    st.markdown("""
    <div class="card">
        <h3>Study guides</h3>
        <p class="small">Turn papers into structured notes, explanations, and review materials for class or research.</p>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown("""
    <div class="card">
        <h3>Flashcards</h3>
        <p class="small">Automatically generate review questions so you actually remember what the paper said.</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

st.header("How it works")

a, b, c = st.columns(3)

with a:
    st.markdown("### 1. Upload")
    st.write("Drop in any academic PDF.")

with b:
    st.markdown("### 2. Analyze")
    st.write("Experra breaks the paper into understandable sections.")

with c:
    st.markdown("### 3. Study")
    st.write("Get summaries, flashcards, limitations, and key insights.")

st.write("")
st.divider()

left, right = st.columns([1.2, 1])

with left:
    st.header("Built for students and researchers")
    st.write(
        "Whether you're reading papers for class, joining a lab, preparing for a journal club, "
        "or trying to understand a field faster, Experra helps you move from PDF overload to usable understanding."
    )

with right:
    st.markdown("""
    <div class="card">
        <h3>Free</h3>
        <div class="price">$0</div>
        <p class="small">3 paper analyses</p>
        <hr>
        <p>✓ Paper summaries</p>
        <p>✓ Study guides</p>
        <p>✓ Flashcards</p>
        <p>✓ Downloadable analysis</p>
    </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

if st.button("Start analyzing papers", type="primary"):
    st.switch_page("pages/1_Analyze_Paper.py")