import logging
import time
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

# Load credentials before importing the pipeline.
load_dotenv(Path(__file__).resolve().parent / ".env")

st.set_page_config(
    page_title="Research Studio",
    page_icon="📚",
    layout="wide",
)

from src.pipelines.pipeline import run_research_pipeline


# ---------- DESIGN ----------
st.markdown("""
<style>
    .block-container {
        max-width: 1150px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    .research-hero {
        background: linear-gradient(120deg, #10243a, #164e63);
        padding: 38px;
        border-radius: 20px;
        margin-bottom: 28px;
        box-shadow: 0 12px 32px rgba(15, 23, 42, 0.12);
    }

    .research-eyebrow {
        color: #67e8f9;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 3px;
        text-transform: uppercase;
    }

    .research-hero h1 {
        color: #ffffff;
        font-size: clamp(30px, 5vw, 46px);
        font-weight: 750;
        letter-spacing: -1.5px;
        margin: 10px 0;
        padding: 0;
    }

    .research-hero p {
        color: #cbd5e1;
        font-size: 16px;
        max-width: 650px;
        line-height: 1.7;
        margin-bottom: 22px;
    }

    .research-badges {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
    }

    .research-badge {
        color: #e2e8f0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        padding: 6px 13px;
        font-size: 12px;
    }

    div[data-testid="stForm"] {
        border-radius: 16px;
        padding: 24px;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: #0e7490;
        color: white;
        border: none;
        border-radius: 10px;
        min-height: 46px;
        font-weight: 600;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #155e75;
        color: white;
    }

    .research-empty {
        text-align: center;
        border: 1px dashed rgba(128, 128, 128, 0.4);
        border-radius: 16px;
        padding: 45px 24px;
        margin-top: 24px;
    }

    .research-empty h3 {
        margin-bottom: 8px;
    }

    .research-empty p {
        opacity: 0.7;
    }

    @media (max-width: 640px) {
        .research-hero {
            padding: 24px;
        }

        .block-container {
            padding-top: 1rem;
        }
    }
</style>
""", unsafe_allow_html=True)


# ---------- SESSION STATE ----------
if "research_result" not in st.session_state:
    st.session_state.research_result = None


# ---------- SIDEBAR ----------
with st.sidebar:
    st.title("Research Studio")
    st.caption("Your research workspace")

    st.markdown("---")
    st.markdown("### How it works")
    st.markdown(
        "1. **Search** for relevant sources.\n"
        "2. **Read** selected webpages.\n"
        "3. **Write** a structured report.\n"
        "4. **Review** its strengths and gaps."
    )

    st.markdown("---")
    st.markdown("### Better topics")
    st.caption(
        "Include a location, timeframe, or specific question "
        "to help focus the research."
    )
    st.markdown(
        "- AI and entry-level jobs in 2026\n"
        "- Solar energy adoption in Pakistan\n"
        "- Benefits and risks of AI in education"
    )

    st.markdown("---")
    st.caption(
        "Reports are AI-generated. Check important claims "
        "against the cited sources."
    )


# ---------- HEADER ----------
st.markdown("""
<div class="research-hero">
    <div class="research-eyebrow">Discover · Understand · Report</div>
    <h1>Turn questions into research.</h1>
    <p>
        Explore a topic, gather web evidence, and generate a structured
        report with a constructive quality review.
    </p>
    <div class="research-badges">
        <span class="research-badge">Web research</span>
        <span class="research-badge">Source references</span>
        <span class="research-badge">Critic feedback</span>
    </div>
</div>
""", unsafe_allow_html=True)


# ---------- INPUT ----------
with st.form("research_form"):
    st.subheader("What would you like to explore?")

    topic = st.text_area(
        "Research topic",
        placeholder=(
            "Example: How is AI affecting entry-level jobs "
            "in the technology industry in 2026?"
        ),
        height=110,
        max_chars=2000,
    )

    st.caption(
        "Be specific about the question you want the report to answer."
    )

    submitted = st.form_submit_button("Generate research report")


# ---------- RUN PIPELINE ----------
if submitted:
    clean_topic = topic.strip()

    if not clean_topic:
        st.warning("Enter a research topic before generating a report.")
    else:
        started = time.perf_counter()

        try:
            with st.spinner(
                "Searching, reading, writing, and reviewing your report..."
            ):
                result = run_research_pipeline(clean_topic)

                if not isinstance(result, dict):
                    raise ValueError("The pipeline must return a dictionary.")

                report = result.get("report")
                feedback = result.get("feedback")

                if not isinstance(report, str) or not report.strip():
                    raise ValueError("The pipeline returned an empty report.")

                if not isinstance(feedback, str) or not feedback.strip():
                    raise ValueError("The pipeline returned empty feedback.")

                st.session_state.research_result = {
                    "topic": clean_topic,
                    "report": report,
                    "feedback": feedback,
                    "search_results": result.get("search_results", ""),
                    "scraped_content": result.get("scraped_content", ""),
                    "duration": time.perf_counter() - started,
                }

            st.success("Your report and review are ready.")

        except Exception:
            logging.exception("Research pipeline failed")
            st.error(
                "The research could not be completed. "
                "Check the error in your terminal, then try again."
            )
            st.stop()


# ---------- DISPLAY RESULTS ----------
saved = st.session_state.research_result

if saved is not None:
    st.markdown("---")
    st.subheader("Research results")
    st.write(saved["topic"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Report words", f"{len(saved['report'].split()):,}")
    col2.metric("Processing time", f"{saved['duration']:.0f} seconds")
    col3.metric("Review", "Completed")

    report_tab, review_tab, notes_tab = st.tabs([
        "Research report",
        "Critic review",
        "Research notes",
    ])

    with report_tab:
        st.download_button(
            label="Download report",
            data=saved["report"],
            file_name="research_report.md",
            mime="text/markdown",
            key="download_report",
        )

        st.markdown(saved["report"], unsafe_allow_html=False)

    with review_tab:
        st.caption(
            "The score is the critic model's assessment, "
            "not independent verification."
        )

        st.download_button(
            label="Download review",
            data=saved["feedback"],
            file_name="research_review.md",
            mime="text/markdown",
            key="download_review",
        )

        st.markdown(saved["feedback"], unsafe_allow_html=False)

    with notes_tab:
        st.caption("The material passed between your research stages.")

        with st.expander("Search results", expanded=True):
            st.markdown(
                saved["search_results"] or "No search results were returned.",
                unsafe_allow_html=False,
            )

        with st.expander("Reader notes"):
            st.markdown(
                saved["scraped_content"] or "No reader notes were returned.",
                unsafe_allow_html=False,
            )

else:
    st.markdown("""
    <div class="research-empty">
        <h3>Your next insight starts with a question.</h3>
        <p>Enter a topic above. Your report and review will appear here.</p>
    </div>
    """, unsafe_allow_html=True)