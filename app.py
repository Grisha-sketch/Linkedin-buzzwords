import streamlit as st
import plotly.express as px
import pandas as pd
from analyzer import analyze_posts, get_frequency_map
from llm import analyze_all_posts

st.set_page_config(
    page_title="LinkedIn Buzzword Analyzer",
    page_icon="🎯",
    layout="wide",
)

st.title("🎯 LinkedIn Buzzword Analyzer")
st.caption("Paste LinkedIn captions below. Separate multiple posts with a blank line or `---`.")

with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1. Paste one or more LinkedIn captions
    2. Or upload a `.txt` file
    3. Click **Analyze**
    4. Get your cringe score
    """)
    st.divider()
    st.markdown("Separate multiple posts with a blank line or `---`")


input_tab, upload_tab = st.tabs(["Paste text", "Upload file"])

raw_text = ""

with input_tab:
    raw_text_input = st.text_area(
        "LinkedIn captions",
        height=250,
        placeholder="Excited to announce that I've leveraged my growth mindset to disrupt the ecosystem...",
    )
    if raw_text_input:
        raw_text = raw_text_input

with upload_tab:
    uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8")
        st.success(f"Loaded file: {uploaded_file.name}")
        st.text_area("Preview", raw_text, height=200, disabled=True)


col1, col2 = st.columns([1, 4])
with col1:
    analyze_btn = st.button("Analyze", type="primary", use_container_width=True)
with col2:
    use_llm = st.toggle("Enable Gemini AI analysis", value=True)


if analyze_btn:
    if not raw_text.strip():
        st.warning("Please paste or upload some text first.")
        st.stop()

    with st.spinner("Detecting buzzwords..."):
        results = analyze_posts(raw_text)

    if not results:
        st.error("No posts detected. Make sure posts are separated by a blank line or `---`.")
        st.stop()

    if use_llm:
        with st.spinner(f"Analyzing {len(results)} post(s) with Gemini..."):
            results = analyze_all_posts(results)

    st.divider()
    st.subheader(f"Results — {len(results)} post(s) analyzed")

    freq_map = get_frequency_map(results)

    if freq_map:
        st.subheader("Buzzword frequency across all posts")
        df = pd.DataFrame(
            list(freq_map.items())[:20],
            columns=["Buzzword", "Count"]
        )
        fig = px.bar(
            df,
            x="Count",
            y="Buzzword",
            orientation="h",
            color="Count",
            color_continuous_scale="Reds",
        )
        fig.update_layout(
            yaxis=dict(autorange="reversed"),
            coloraxis_showscale=False,
            margin=dict(l=0, r=0, t=0, b=0),
            height=max(300, len(df) * 28),
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No buzzwords detected across any posts.")

    st.divider()
    st.subheader("Per-post breakdown")

    for result in results:
        post_preview = result["text"][:60] + "..." if len(result["text"]) > 60 else result["text"]
        rule_score = result["rule_based_score"]

        if use_llm and result.get("gemini", {}).get("success"):
            cringe_score = result["gemini"]["data"]["cringe_score"]
        else:
            cringe_score = rule_score

        if cringe_score <= 20:
            badge = "🟢 Genuine"
        elif cringe_score <= 40:
            badge = "🟡 Mild Jargon"
        elif cringe_score <= 60:
            badge = "🟠 Corporate Tone"
        elif cringe_score <= 80:
            badge = "🔴 Heavy Jargon"
        else:
            badge = "💀 Peak LinkedIn"

        with st.expander(f"Post {result['index']} — {badge} ({cringe_score}/100) — {post_preview}"):

            st.markdown("**Original post**")
            st.text(result["text"])

            st.divider()

            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Cringe Score", f"{cringe_score}/100")
            with col_b:
                st.metric("Buzzwords found", len(result["buzzwords"]))

            if result["buzzwords"]:
                st.markdown("**Buzzwords detected**")
                buzzword_tags = " ".join(
                    [f"`{item['buzzword']}` ×{item['count']}" for item in result["buzzwords"]]
                )
                st.markdown(buzzword_tags)

            if use_llm:
                gemini = result.get("gemini", {})
                if gemini.get("success"):
                    data = gemini["data"]
                    st.divider()
                    st.markdown("**Gemini verdict**")
                    st.info(data["verdict"])

                    st.markdown("**Why it feels corporate**")
                    for reason in data["reasons"]:
                        st.markdown(f"- {reason}")

                    st.markdown("**Suggested rewrite**")
                    st.success(data["rewrite"])
                else:
                    st.warning(f"Gemini error: {gemini.get('error', 'Unknown error')}")