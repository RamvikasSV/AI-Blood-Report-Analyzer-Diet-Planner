import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
from pathlib import Path

# Load environment variables
load_dotenv()

# Set up page config
st.set_page_config(
    page_title="Blood Work Analysis Pipeline",
    page_icon="🩺",
    layout="wide"
)

st.title("🩺 Blood Work Analysis Pipeline")
st.markdown("A two-stage LLM pipeline for comprehensive health analysis")

# User notice about API limits
st.info("If you encounter API limit or key errors (e.g. rate limit or quota exceeded), please wait a few minutes and try again.")

# Initialize LLM
@st.cache_resource
def load_llm():
    return ChatGoogleGenerativeAI(model="gemma-4-31b-it")

llm = load_llm()

# Load blood work data (robust lookup for deployed environments)
@st.cache_data
def load_blood_report():
    # Try several candidate locations relative to this file and the current working dir
    candidates = [
        Path(__file__).resolve().parent.parent / "blood_work.txt",  # repo root when running from streamlit_app
        Path(__file__).resolve().parent / ".." / "blood_work.txt",
        Path.cwd() / "blood_work.txt",
    ]
    for p in candidates:
        try:
            p = p.resolve()
            if p.exists():
                with open(p, "r", encoding="utf-8") as f:
                    return f.read()
        except Exception:
            continue
    return None

demo_blood_report = load_blood_report()

# Reset and initialize session state
if "mode" not in st.session_state:
    st.session_state.mode = None
    st.session_state.blood_report = None
    st.session_state.analysis_mode = "Quick summary + diet plan"
    st.session_state.extracted_values = None
    st.session_state.diet_plan = None
    st.session_state.quick_done = False
    st.session_state.step_done = False

# Data source selection
st.markdown("### 📂 Select Data Source")
source = st.radio(
    "Choose input type:",
    ["Demo (Built-in Dataset)", "Custom Blood Report"],
    horizontal=True,
    key="data_source"
)

# Reset results when data source changes
if st.session_state.get("last_source") != source:
    st.session_state.last_source = source
    st.session_state.quick_done = False
    st.session_state.step_done = False
    st.session_state.extracted_values = None
    st.session_state.diet_plan = None

blood_report = None
if source == "Demo (Built-in Dataset)":
    if demo_blood_report is None:
        st.error("⚠️ blood_work.txt file not found. Please ensure it's in the parent directory.")
        st.stop()
    st.success("✅ Using Demo Dataset (Rajesh Sharma's Blood Work)")
    blood_report = demo_blood_report
else:
    st.subheader("Enter Your Blood Report")
    custom_text = st.text_area(
        "Paste your blood report here:",
        height=200,
        placeholder="Enter patient blood work report with test values and reference ranges..."
    )
    if custom_text:
        blood_report = custom_text

if blood_report is not None:
    st.session_state.blood_report = blood_report
else:
    st.session_state.blood_report = None

# Analysis mode selection
if st.session_state.blood_report:
    st.markdown("### ⚡ Choose Analysis Mode")
    analysis_mode = st.radio(
        "How do you want the analysis?",
        ["Quick summary + diet plan", "Show step-by-step analysis"],
        horizontal=True,
        key="analysis_mode"
    )

    if st.session_state.analysis_mode != analysis_mode:
        st.session_state.analysis_mode = analysis_mode
        st.session_state.quick_done = False
        st.session_state.step_done = False
        st.session_state.extracted_values = None
        st.session_state.diet_plan = None

    with st.expander("📋 View Blood Report", expanded=False):
        st.text(st.session_state.blood_report)

    if analysis_mode == "Quick summary + diet plan":
        st.markdown("Use the quick mode to get a summary and diet plan instantly. If you want to see the extraction details, choose step-by-step mode.")
        if st.button("▶️ Run Quick Analysis", key="quick_run"):
            with st.spinner("Running quick analysis..."):
                extraction_prompt = f"""
You are a medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as HIGH, LOW, or NORMAL 
based on the reference ranges provided in the report.

Format your response as:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{st.session_state.blood_report}
"""
                extraction_response = llm.invoke(extraction_prompt)
                st.session_state.extracted_values = extraction_response.text

                diet_prompt = f"""
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, write:
1. A short health summary in 4-5 lines explaining the patient's condition in simple language
2. A short, practical Indian diet plan having only two sections (1) Foods to avoid (2) Foods to eat more of.
   Do not include any other sections in diet plan.

Blood Work Analysis:
{st.session_state.extracted_values}
"""
                diet_response = llm.invoke(diet_prompt)
                st.session_state.diet_plan = diet_response.text
                st.session_state.quick_done = True
                st.session_state.step_done = False
                st.success("✅ Quick analysis complete!")

        if st.session_state.quick_done and st.session_state.diet_plan:
            st.subheader("📝 Health Summary & Diet Plan")
            st.markdown(st.session_state.diet_plan)
            with st.expander("Show extraction details", expanded=False):
                st.text_area("Extracted Values:", value=st.session_state.extracted_values, height=260, disabled=True)

    else:
        st.markdown("Follow the step-by-step flow to extract values first and then generate the summary.")

        st.divider()
        st.header("Stage 1️⃣: Extract and Flag Abnormal Values")
        st.markdown("Extracting all test values and classifying them based on reference ranges...")

        if st.button("🔍 Extract Blood Work Values", key="extract_btn"):
            with st.spinner("Processing Stage 1..."):
                extraction_prompt = f"""
You are a medical data extraction assistant.

From the blood report below, extract ALL test values and classify each one as HIGH, LOW, or NORMAL 
based on the reference ranges provided in the report.

Format your response as:
- Test Name: value | Status: HIGH/LOW/NORMAL | Reference: range

Blood Report:
{st.session_state.blood_report}
"""
                extraction_response = llm.invoke(extraction_prompt)
                st.session_state.extracted_values = extraction_response.text
                st.success("✅ Stage 1 Complete!")

        if st.session_state.extracted_values:
            st.subheader("📊 Extracted Blood Work Values")
            st.text_area("Extracted Values:", value=st.session_state.extracted_values, height=300, disabled=True)

            st.divider()
            st.header("Stage 2️⃣: Health Summary & Indian Diet Plan")
            st.markdown("Generating personalized health summary and diet recommendations...")
            if st.button("🍽️ Generate Health Summary & Diet Plan", key="diet_btn"):
                with st.spinner("Processing Stage 2..."):
                    diet_prompt = f"""
You are a clinical nutritionist specializing in Indian dietary habits.

Based on the blood work analysis below, write:
1. A short health summary in 4-5 lines explaining the patient's condition in simple language
2. A short, practical Indian diet plan having only two sections (1) Foods to avoid (2) Foods to eat more of.
   Do not include any other sections in diet plan.

Blood Work Analysis:
{st.session_state.extracted_values}
"""
                    diet_response = llm.invoke(diet_prompt)
                    st.session_state.diet_plan = diet_response.text
                    st.session_state.step_done = True
                    st.success("✅ Stage 2 Complete!")

        if st.session_state.step_done and st.session_state.diet_plan:
            st.subheader("📝 Health Summary & Diet Plan")
            st.markdown(st.session_state.diet_plan)

    if (st.session_state.quick_done or st.session_state.step_done) and st.session_state.diet_plan:
        st.divider()
        if st.button("🔄 New Analysis / New Entry", key="new_analysis_btn", use_container_width=True):
            st.session_state.clear()
            st.session_state.quick_done = False
            st.session_state.step_done = False
            st.session_state.analysis_mode = "Quick summary + diet plan"
            st.session_state.blood_report = None
            st.session_state.data_source = "Demo (Built-in Dataset)"
            # After button click, Streamlit reruns automatically with cleared state.
else:
    st.warning("⚠️ Please select a data source and enter the report before continuing.")

st.divider()

# Footer
st.markdown("""
---
**Disclaimer:** This application is for informational purposes only and should not replace professional medical advice. 
Always consult with a healthcare provider for personalized medical guidance.
""")
