import streamlit as st
from analyzer import analyze_posts, get_frequency_map
from llm import analyze_all_posts

st.set_page_config(
    page_title="LinkedIn Buzzword Analyzer",
    page_icon="🎯",
    layout="wide",
)

st.markdown("""
<style>
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 10px;
    margin-bottom: 1.5rem;
}
.metric-card {
    background: rgba(128,128,128,0.1);
    border: 0.5px solid rgba(128,128,128,0.2);
    border-radius: 8px;
    padding: 14px 16px;
}
.metric-label {
    font-size: 12px;
    color: rgba(128,128,128,0.9);
    margin: 0 0 4px;
}
.metric-value {
    font-size: 22px;
    font-weight: 600;
    margin: 0;
}
.metric-sub {
    font-size: 11px;
    color: rgba(128,128,128,0.7);
    margin: 4px 0 0;
}
.section-title {
    font-size: 12px;
    font-weight: 600;
    color: rgba(128,128,128,0.9);
    text-transform: uppercase;
    letter-spacing: .05em;
    margin: 0 0 10px;
}
.bar-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}
.bar-label {
    font-size: 13px;
    min-width: 140px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.bar-track {
    flex: 1;
    height: 6px;
    background: rgba(128,128,128,0.15);
    border-radius: 3px;
    overflow: hidden;
}
.bar-num {
    font-size: 12px;
    font-weight: 600;
    min-width: 28px;
    text-align: right;
}
.post-card {
    background: rgba(128,128,128,0.05);
    border: 0.5px solid rgba(128,128,128,0.2);
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 12px;
}
.post-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 6px;
}
.post-title {
    font-size: 14px;
    font-weight: 600;
    margin: 0;
}
.post-excerpt {
    font-size: 13px;
    color: rgba(128,128,128,0.9);
    line-height: 1.6;
    border-left: 2px solid rgba(128,128,128,0.3);
    padding-left: 10px;
    margin: 0 0 10px;
}
.score-badge {
    font-size: 13px;
    font-weight: 600;
    padding: 4px 12px;
    border-radius: 20px;
}
.tags {
    display: flex;
    flex-wrap: wrap;
    gap: 6px;
    margin-bottom: 10px;
}
.tag {
    font-size: 11px;
    padding: 3px 8px;
    border-radius: 20px;
    background: rgba(220,38,38,0.15);
    color: #f87171;
}
.verdict-box {
    font-size: 13px;
    background: rgba(128,128,128,0.1);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
    line-height: 1.5;
}
.verdict-label {
    font-size: 11px;
    font-weight: 600;
    color: rgba(128,128,128,0.7);
    display: block;
    margin-bottom: 4px;
}
.rewrite-box {
    font-size: 13px;
    background: rgba(74,156,47,0.15);
    border-radius: 8px;
    padding: 10px 12px;
    line-height: 1.5;
    color: #86efac;
}
.rewrite-label {
    font-size: 11px;
    font-weight: 600;
    color: #4ade80;
    display: block;
    margin-bottom: 4px;
}
.reasons-box {
    font-size: 13px;
    background: rgba(128,128,128,0.1);
    border-radius: 8px;
    padding: 10px 12px;
    margin-bottom: 10px;
    line-height: 1.6;
}
.divider {
    border: none;
    border-top: 0.5px solid rgba(128,128,128,0.2);
    margin: 1.2rem 0;
}
</style>
""", unsafe_allow_html=True)


def score_color(score):
    if score <= 20:
        return "#4a9c2f", "#d4edbc", "#27500A"
    elif score <= 40:
        return "#c47f17", "#fde8b0", "#7a4f0a"
    elif score <= 60:
        return "#d97706", "#fef3c7", "#92400e"
    elif score <= 80:
        return "#dc2626", "#fee2e2", "#991b1b"
    else:
        return "#991b1b", "#fee2e2", "#7f1d1d"


def score_label(score):
    if score <= 20:
        return "Genuine 🟢"
    elif score <= 40:
        return "Mild jargon 🟡"
    elif score <= 60:
        return "Corporate tone 🟠"
    elif score <= 80:
        return "Heavy jargon 🔴"
    else:
        return "Peak LinkedIn 💀"


def render_metric_cards(results, freq_map):
    scores = []
    for r in results:
        if r.get("gemini", {}).get("success"):
            scores.append(r["gemini"]["data"]["cringe_score"])
        else:
            scores.append(r["rule_based_score"])

    avg_score = int(sum(scores) / len(scores)) if scores else 0
    total_buzzwords = sum(len(r["buzzwords"]) for r in results)
    top_word = list(freq_map.keys())[0] if freq_map else "none"
    top_count = freq_map.get(top_word, 0)
    peak_count = sum(1 for s in scores if s >= 80)
    avg_color, _, _ = score_color(avg_score)

    st.markdown(f"""
    <div class="metric-grid">
        <div class="metric-card">
            <p class="metric-label">Average cringe score</p>
            <p class="metric-value" style="color:{avg_color}">{avg_score}/100</p>
            <p class="metric-sub">across {len(results)} post(s)</p>
        </div>
        <div class="metric-card">
            <p class="metric-label">Total buzzwords</p>
            <p class="metric-value">{total_buzzwords}</p>
            <p class="metric-sub">unique hits</p>
        </div>
        <div class="metric-card">
            <p class="metric-label">Most used</p>
            <p class="metric-value"
            style="font-size:16px;padding-top:5px">{top_word}</p>
            <p class="metric-sub">&times;{top_count} across posts</p>
        </div>
        <div class="metric-card">
            <p class="metric-label">Peak LinkedIn 💀</p>
            <p class="metric-value">{peak_count}</p>
            <p class="metric-sub">post(s) scored 80+</p>
        </div>
    </div>
    """, unsafe_allow_html=True)


def render_score_bars(results, freq_map):
    st.markdown(
        '<p class="section-title">Cringe leaderboard</p>',
        unsafe_allow_html=True
    )
    for r in results:
        if r.get("gemini", {}).get("success"):
            score = r["gemini"]["data"]["cringe_score"]
        else:
            score = r["rule_based_score"]

        bar_color, _, _ = score_color(score)
        st.markdown(f"""
        <div class="bar-row">
            <span class="bar-label">Post {r['index']}</span>
            <div class="bar-track">
                <div style="width:{score}%;height:100%;
                background:{bar_color};border-radius:3px"></div>
            </div>
            <span class="bar-num" style="color:{bar_color}">{score}</span>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-title">Top buzzwords across all posts</p>',
        unsafe_allow_html=True
    )

    top_words = list(freq_map.items())[:8]
    max_count = top_words[0][1] if top_words else 1
    for word, count in top_words:
        pct = int((count / max_count) * 100)
        st.markdown(f"""
        <div class="bar-row">
            <span class="bar-label">{word}</span>
            <div class="bar-track">
                <div style="width:{pct}%;height:100%;
                background:#7F77DD;border-radius:3px"></div>
            </div>
            <span class="bar-num" style="color:#534AB7">&times;{count}</span>
        </div>
        """, unsafe_allow_html=True)


def render_post_card(result, use_llm):
    if use_llm and result.get("gemini", {}).get("success"):
        score = result["gemini"]["data"]["cringe_score"]
    else:
        score = result["rule_based_score"]

    bar_color, badge_bg, badge_text = score_color(score)
    label = score_label(score)
    excerpt = (
        result["text"][:120] + "..."
        if len(result["text"]) > 120
        else result["text"]
    )

    tags_html = "".join(
        f'<span class="tag">{item["buzzword"]} &times;{item["count"]}</span>'
        for item in result["buzzwords"]
    )
    no_tags = '<span style="font-size:12px;color:rgba(128,128,128,0.6)">'\
              'No buzzwords detected</span>'

    gemini_html = ""
    if use_llm:
        gemini = result.get("gemini", {})
        if gemini.get("success"):
            data = gemini["data"]
            reasons_html = "".join(
                f"<li>{r}</li>" for r in data["reasons"]
            )
            gemini_html = (
                '<div class="verdict-box">'
                '<span class="verdict-label">Gemini verdict</span>'
                + data["verdict"]
                + "</div>"
                '<div class="reasons-box">'
                '<span class="verdict-label">Why it feels corporate</span>'
                f'<ul style="margin:0;padding-left:16px">{reasons_html}</ul>'
                "</div>"
                '<div class="rewrite-box">'
                '<span class="rewrite-label">Suggested rewrite</span>'
                + data["rewrite"]
                + "</div>"
            )
        else:
            import html
            safe_err = html.escape(
                str(gemini.get("error", "Unknown error"))
            )[:200]
            gemini_html = (
                '<div class="verdict-box" style="color:#f87171">'
                '<span class="verdict-label">Gemini error</span>'
                + safe_err
                + "</div>"
            )

    post_num = result["index"]
    st.markdown(f"""
    <div class="post-card">
        <div class="post-header">
            <p class="post-title">Post {post_num}
                <span style="font-size:12px;
                color:rgba(128,128,128,0.7);font-weight:400">
                &middot; {label}</span>
            </p>
            <span class="score-badge"
            style="background:{badge_bg};color:{badge_text}">
                {score}/100
            </span>
        </div>
        <p class="post-excerpt">{excerpt}</p>
        <div class="tags">{tags_html if tags_html else no_tags}</div>
        {gemini_html}
    </div>
    """, unsafe_allow_html=True)


st.markdown("## 🎯 LinkedIn buzzword analyzer")
st.caption(
    "Paste captions below. "
    "Separate multiple posts with a blank line or `---`."
)

with st.sidebar:
    st.header("How to use")
    st.markdown("""
    1. Paste one or more LinkedIn captions
    2. Or upload a `.txt` file
    3. Toggle Gemini AI on or off
    4. Click **Analyze**
    """)
    st.divider()
    st.markdown("**Score guide**")
    st.markdown("""
    - 🟢 0–20 · Genuine
    - 🟡 21–40 · Mild jargon
    - 🟠 41–60 · Corporate tone
    - 🔴 61–80 · Heavy jargon
    - 💀 81–100 · Peak LinkedIn
    """)

input_tab, upload_tab = st.tabs(["Paste text", "Upload file"])
raw_text = ""

with input_tab:
    placeholder = (
        "Excited to announce I've leveraged my growth mindset "
        "to disrupt the ecosystem..."
    )
    raw_text_input = st.text_area(
        "LinkedIn captions",
        height=220,
        placeholder=placeholder,
    )
    if raw_text_input:
        raw_text = raw_text_input

with upload_tab:
    uploaded_file = st.file_uploader("Upload a .txt file", type=["txt"])
    if uploaded_file:
        raw_text = uploaded_file.read().decode("utf-8")
        st.success(f"Loaded: {uploaded_file.name}")
        st.text_area("Preview", raw_text, height=180, disabled=True)

col1, col2 = st.columns([1, 4])
with col1:
    analyze_btn = st.button(
        "Analyze", type="primary", use_container_width=True
    )
with col2:
    use_llm = st.toggle("Enable Gemini AI analysis", value=True)

if analyze_btn:
    if not raw_text.strip():
        st.warning("Please paste or upload some text first.")
        st.stop()

    with st.spinner("Detecting buzzwords..."):
        results = analyze_posts(raw_text)

    if not results:
        st.error(
            "No posts detected. "
            "Separate posts with a blank line or `---`."
        )
        st.stop()

    if use_llm:
        with st.spinner(
            f"Analyzing {len(results)} post(s) with Gemini..."
        ):
            results = analyze_all_posts(results)

    st.divider()

    freq_map = get_frequency_map(results)
    render_metric_cards(results, freq_map)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    render_score_bars(results, freq_map)

    st.markdown('<hr class="divider">', unsafe_allow_html=True)
    st.markdown(
        '<p class="section-title">Per-post breakdown</p>',
        unsafe_allow_html=True
    )

    for result in results:
        render_post_card(result, use_llm)
