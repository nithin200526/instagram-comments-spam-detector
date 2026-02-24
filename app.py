"""
🛡️ Intelligent Social Media Spam Detection System
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Streamlit web app for real-time spam comment detection
with dashboard analytics, spam folder, and manual override.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import os
import sys

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from src.predict import predict

# ─── Page Config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="🛡️ Spam Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
    /* ── Global ────────────────────────────────── */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* ── Hero Header ───────────────────────────── */
    .hero-header {
        background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
        padding: 2.5rem 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        box-shadow: 0 20px 60px rgba(48, 43, 99, 0.4);
        position: relative;
        overflow: hidden;
    }
    .hero-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(139, 92, 246, 0.1) 0%, transparent 70%);
        animation: pulse 4s ease-in-out infinite;
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); opacity: 0.5; }
        50% { transform: scale(1.1); opacity: 1; }
    }
    .hero-header h1 {
        color: #fff;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0;
        position: relative;
        text-shadow: 0 0 30px rgba(139, 92, 246, 0.5);
    }
    .hero-header p {
        color: #a5b4fc;
        font-size: 1rem;
        margin-top: 0.5rem;
        position: relative;
    }
    
    /* ── Result Cards ──────────────────────────── */
    .result-card {
        padding: 2rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        transition: transform 0.3s ease;
    }
    .result-card:hover {
        transform: translateY(-4px);
    }
    .result-spam {
        background: linear-gradient(135deg, #dc2626, #991b1b);
        color: white;
    }
    .result-safe {
        background: linear-gradient(135deg, #059669, #047857);
        color: white;
    }
    .result-label {
        font-size: 2rem;
        font-weight: 800;
        margin: 0.5rem 0;
    }
    .result-confidence {
        font-size: 1.1rem;
        opacity: 0.9;
    }
    
    /* ── Stat Cards ────────────────────────────── */
    .stat-card {
        background: linear-gradient(135deg, #1e1b4b, #312e81);
        padding: 1.5rem;
        border-radius: 16px;
        text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        border: 1px solid rgba(139, 92, 246, 0.2);
    }
    .stat-card h3 {
        color: #a5b4fc;
        font-size: 0.85rem;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0;
    }
    .stat-card .stat-value {
        color: #fff;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0.3rem 0;
    }
    
    /* ── History Table ──────────────────────────── */
    .history-row {
        background: rgba(30, 27, 75, 0.5);
        padding: 1rem 1.5rem;
        border-radius: 12px;
        margin-bottom: 0.5rem;
        border-left: 4px solid;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    .history-spam { border-color: #ef4444; }
    .history-safe { border-color: #10b981; }
    
    /* ── Sidebar ───────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0c29, #1e1b4b);
    }
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3 {
        color: #e0e7ff;
    }
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown li {
        color: #a5b4fc;
    }
    
    /* ── Tab styling ───────────────────────────── */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        padding: 8px 20px;
        font-weight: 600;
    }
    
    /* ── Button ─────────────────────────────────── */
    .stButton > button {
        background: linear-gradient(135deg, #7c3aed, #6d28d9);
        color: white;
        border: none;
        padding: 0.7rem 2rem;
        border-radius: 12px;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(124, 58, 237, 0.4);
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #6d28d9, #5b21b6);
        box-shadow: 0 6px 20px rgba(124, 58, 237, 0.6);
        transform: translateY(-2px);
    }
    
    /* ── Badge ──────────────────────────────────── */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .badge-spam { background: #fecaca; color: #991b1b; }
    .badge-safe { background: #d1fae5; color: #065f46; }
    .badge-override { background: #fef3c7; color: #92400e; }
</style>
""", unsafe_allow_html=True)


# ─── Session State ────────────────────────────────────────────────────────────
if "history" not in st.session_state:
    st.session_state.history = []  # List of dicts: {text, label, confidence, spam_prob, time, overridden, original_label}
if "auto_hide_threshold" not in st.session_state:
    st.session_state.auto_hide_threshold = 0.80


# ─── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Settings")
    st.session_state.auto_hide_threshold = st.slider(
        "Auto-Hide Threshold",
        min_value=0.50,
        max_value=0.99,
        value=st.session_state.auto_hide_threshold,
        step=0.01,
        help="Comments with spam probability above this threshold are auto-flagged."
    )
    
    st.markdown("---")
    st.markdown("## 📖 About")
    st.markdown("""
    **Spam Detector** uses Machine Learning to classify social media comments as spam or legitimate.
    
    **Features:**
    - 🔍 Real-time classification
    - 📊 Dashboard analytics
    - 📁 Spam folder
    - 🔄 Manual override
    - ⚡ Auto-hide flagging
    """)
    
    st.markdown("---")
    st.markdown("## 🧠 Model Info")
    model_info_path = os.path.join(os.path.dirname(__file__), "models", "training_summary.joblib")
    if os.path.exists(model_info_path):
        import joblib
        summary = joblib.load(model_info_path)
        st.success(f"**Model:** {summary['best_model']}")
        metrics = summary["metrics"][summary["best_model"]]
        st.metric("Accuracy", f"{metrics['accuracy']:.1%}")
        st.metric("Precision", f"{metrics['precision']:.1%}")
        st.metric("F1 Score", f"{metrics['f1']:.1%}")
    else:
        st.warning("Model not trained yet. Run `python -m src.model` first.")
    
    st.markdown("---")
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.rerun()


# ─── Hero Header ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <h1>🛡️ Intelligent Spam Detector</h1>
    <p>AI-powered social media comment classification with real-time analytics</p>
</div>
""", unsafe_allow_html=True)


# ─── Tabs ─────────────────────────────────────────────────────────────────────
tab_detect, tab_history, tab_spam, tab_dashboard = st.tabs([
    "🔍 Detect Spam",
    "📜 History",
    "📁 Spam Folder",
    "📊 Dashboard"
])


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1: DETECT SPAM
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_detect:
    st.markdown("### 💬 Enter a Comment to Analyze")
    
    col_input, col_examples = st.columns([3, 1])
    
    with col_input:
        comment_text = st.text_area(
            "Type or paste a comment:",
            height=120,
            placeholder="e.g., 'Check out my channel for free gifts!' or 'Great video, very helpful!'",
            label_visibility="collapsed",
        )
    
    with col_examples:
        st.markdown("**Quick Examples:**")
        example_spam = [
            "FREE iPhone! Go to bit.ly/free 🔥",
            "Sub4Sub! Subscribe to me!!!",
            "I made $5000 in a week! DM me",
        ]
        example_ham = [
            "Great tutorial, thanks!",
            "This was really helpful",
            "Love the editing on this",
        ]
        
        st.markdown("🚫 **Spam:**")
        for ex in example_spam:
            if st.button(ex, key=f"spam_{ex[:15]}", use_container_width=True):
                comment_text = ex
        
        st.markdown("✅ **Legit:**")
        for ex in example_ham:
            if st.button(ex, key=f"ham_{ex[:15]}", use_container_width=True):
                comment_text = ex
    
    if st.button("🔍 Analyze Comment", use_container_width=True, type="primary"):
        if comment_text.strip():
            with st.spinner("Analyzing..."):
                result = predict(comment_text.strip())
            
            is_spam = result["label"] == "Spam"
            auto_hidden = result["spam_probability"] >= st.session_state.auto_hide_threshold
            
            # Store in history
            entry = {
                "text": comment_text.strip(),
                "label": result["label"],
                "confidence": result["confidence"],
                "spam_probability": result["spam_probability"],
                "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "overridden": False,
                "original_label": result["label"],
                "auto_hidden": auto_hidden and is_spam,
                "cleaned_text": result["cleaned_text"],
            }
            st.session_state.history.insert(0, entry)
            
            # Display result
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if is_spam:
                    st.markdown(f"""
                    <div class="result-card result-spam">
                        <div style="font-size: 3rem;">🚫</div>
                        <div class="result-label">SPAM DETECTED</div>
                        <div class="result-confidence">Confidence: {result['confidence']:.1%}</div>
                        <div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.8;">
                            Spam Probability: {result['spam_probability']:.1%}
                        </div>
                        {'<div style="margin-top: 1rem;"><span class="badge badge-override">⚡ AUTO-HIDDEN</span></div>' if auto_hidden else ''}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div class="result-card result-safe">
                        <div style="font-size: 3rem;">✅</div>
                        <div class="result-label">SAFE COMMENT</div>
                        <div class="result-confidence">Confidence: {result['confidence']:.1%}</div>
                        <div style="margin-top: 0.5rem; font-size: 0.9rem; opacity: 0.8;">
                            Spam Probability: {result['spam_probability']:.1%}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.warning("⚠️ Please enter a comment to analyze.")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2: HISTORY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_history:
    st.markdown("### 📜 Prediction History")
    
    if not st.session_state.history:
        st.info("No predictions yet. Go to the **Detect Spam** tab to analyze comments.")
    else:
        # Stats row
        total = len(st.session_state.history)
        spam_count = sum(1 for h in st.session_state.history if h["label"] == "Spam")
        safe_count = total - spam_count
        override_count = sum(1 for h in st.session_state.history if h["overridden"])
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><h3>Total</h3><div class="stat-value">{total}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><h3>Spam</h3><div class="stat-value" style="color:#f87171;">{spam_count}</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><h3>Safe</h3><div class="stat-value" style="color:#34d399;">{safe_count}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card"><h3>Overridden</h3><div class="stat-value" style="color:#fbbf24;">{override_count}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        for i, entry in enumerate(st.session_state.history):
            is_spam = entry["label"] == "Spam"
            border_class = "history-spam" if is_spam else "history-safe"
            badge_class = "badge-spam" if is_spam else "badge-safe"
            badge_text = "SPAM" if is_spam else "SAFE"
            
            col_text, col_meta, col_action = st.columns([4, 2, 1])
            
            with col_text:
                override_tag = " 🔄" if entry["overridden"] else ""
                auto_tag = " ⚡" if entry.get("auto_hidden") else ""
                st.markdown(f"**{entry['text'][:100]}{'...' if len(entry['text']) > 100 else ''}**{override_tag}{auto_tag}")
            
            with col_meta:
                emoji = "🚫" if is_spam else "✅"
                st.markdown(f"{emoji} **{entry['label']}** ({entry['confidence']:.0%}) — {entry['time']}")
            
            with col_action:
                new_label = "Not Spam" if is_spam else "Spam"
                if st.button(f"Mark as {new_label}", key=f"override_{i}"):
                    st.session_state.history[i]["label"] = new_label
                    st.session_state.history[i]["overridden"] = True
                    st.rerun()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3: SPAM FOLDER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_spam:
    st.markdown("### 📁 Spam Folder")
    st.markdown("Comments flagged as spam are stored here. You can review and override them.")
    
    spam_entries = [
        (i, entry) for i, entry in enumerate(st.session_state.history)
        if entry["label"] == "Spam"
    ]
    
    if not spam_entries:
        st.info("🎉 No spam detected yet! Your feed looks clean.")
    else:
        st.markdown(f"**{len(spam_entries)}** comment(s) flagged as spam")
        st.markdown("---")
        
        for idx, (i, entry) in enumerate(spam_entries):
            with st.container():
                col1, col2, col3 = st.columns([5, 2, 1])
                
                with col1:
                    auto_tag = "⚡ Auto-hidden | " if entry.get("auto_hidden") else ""
                    override_tag = "🔄 Overridden | " if entry.get("overridden") else ""
                    st.markdown(f"**{entry['text']}**")
                    st.caption(f"{auto_tag}{override_tag}Spam probability: {entry['spam_probability']:.1%} | {entry['time']}")
                
                with col2:
                    st.markdown(f"Confidence: **{entry['confidence']:.1%}**")
                
                with col3:
                    if st.button("✅ Mark Safe", key=f"safe_{i}_{idx}"):
                        st.session_state.history[i]["label"] = "Not Spam"
                        st.session_state.history[i]["overridden"] = True
                        st.rerun()
            
            st.markdown("---")


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4: DASHBOARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab_dashboard:
    st.markdown("### 📊 Analytics Dashboard")
    
    if not st.session_state.history:
        st.info("No data to display yet. Analyze some comments first!")
    else:
        history_df = pd.DataFrame(st.session_state.history)
        
        # ── Stats Row ──────────────────────────────────────────────────
        spam_count = (history_df["label"] == "Spam").sum()
        safe_count = (history_df["label"] == "Not Spam").sum()
        avg_confidence = history_df["confidence"].mean()
        auto_hidden = history_df.get("auto_hidden", pd.Series([False])).sum()
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f'<div class="stat-card"><h3>Total Analyzed</h3><div class="stat-value">{len(history_df)}</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><h3>Spam Rate</h3><div class="stat-value" style="color:#f87171;">{spam_count/(spam_count+safe_count)*100:.0f}%</div></div>', unsafe_allow_html=True)
        with c3:
            st.markdown(f'<div class="stat-card"><h3>Avg Confidence</h3><div class="stat-value">{avg_confidence:.0%}</div></div>', unsafe_allow_html=True)
        with c4:
            st.markdown(f'<div class="stat-card"><h3>Auto-Hidden</h3><div class="stat-value" style="color:#fbbf24;">{int(auto_hidden)}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        
        # ── Charts ─────────────────────────────────────────────────────
        col_pie, col_bar = st.columns(2)
        
        with col_pie:
            st.markdown("#### 🥧 Spam vs. Legitimate")
            fig_pie = px.pie(
                values=[spam_count, safe_count],
                names=["Spam", "Legitimate"],
                color_discrete_sequence=["#ef4444", "#10b981"],
                hole=0.45,
            )
            fig_pie.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e7ff", family="Inter"),
                showlegend=True,
                margin=dict(t=20, b=20, l=20, r=20),
                height=350,
            )
            fig_pie.update_traces(
                textposition="inside",
                textinfo="percent+label",
                textfont_size=14,
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col_bar:
            st.markdown("#### 📈 Confidence Distribution")
            fig_hist = px.histogram(
                history_df,
                x="spam_probability",
                nbins=20,
                color="label",
                color_discrete_map={"Spam": "#ef4444", "Not Spam": "#10b981"},
                barmode="overlay",
                labels={"spam_probability": "Spam Probability", "label": "Classification"},
            )
            fig_hist.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#e0e7ff", family="Inter"),
                xaxis=dict(gridcolor="rgba(139,92,246,0.1)"),
                yaxis=dict(gridcolor="rgba(139,92,246,0.1)"),
                margin=dict(t=20, b=40, l=40, r=20),
                height=350,
            )
            fig_hist.update_traces(opacity=0.7)
            st.plotly_chart(fig_hist, use_container_width=True)
        
        # ── Word Cloud ─────────────────────────────────────────────────
        st.markdown("#### ☁️ Spam Word Cloud")
        spam_texts = history_df[history_df["label"] == "Spam"]["cleaned_text"]
        if len(spam_texts) > 0 and spam_texts.str.strip().any():
            from wordcloud import WordCloud
            import matplotlib.pyplot as plt
            
            all_spam_text = " ".join(spam_texts.dropna().tolist())
            if all_spam_text.strip():
                wc = WordCloud(
                    width=800,
                    height=300,
                    background_color="rgba(255,255,255,0)",
                    mode="RGBA",
                    colormap="Reds",
                    max_words=80,
                    prefer_horizontal=0.7,
                ).generate(all_spam_text)
                
                fig_wc, ax = plt.subplots(figsize=(12, 4))
                ax.imshow(wc, interpolation="bilinear")
                ax.axis("off")
                fig_wc.patch.set_alpha(0.0)
                st.pyplot(fig_wc)
            else:
                st.info("Not enough spam text for word cloud.")
        else:
            st.info("No spam comments to generate word cloud from.")
        
        # ── Timeline ───────────────────────────────────────────────────
        st.markdown("#### 📅 Detection Timeline")
        timeline_df = history_df.copy()
        timeline_df["time"] = pd.to_datetime(timeline_df["time"])
        timeline_df = timeline_df.sort_values("time")
        
        fig_timeline = go.Figure()
        for label, color in [("Spam", "#ef4444"), ("Not Spam", "#10b981")]:
            mask = timeline_df["label"] == label
            subset = timeline_df[mask]
            if len(subset) > 0:
                fig_timeline.add_trace(go.Scatter(
                    x=subset["time"],
                    y=subset["spam_probability"],
                    mode="markers+lines",
                    name=label,
                    marker=dict(color=color, size=10),
                    line=dict(color=color, width=2),
                    hovertemplate="%{text}<br>Spam Prob: %{y:.1%}<extra></extra>",
                    text=subset["text"].str[:50],
                ))
        
        fig_timeline.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e0e7ff", family="Inter"),
            xaxis=dict(gridcolor="rgba(139,92,246,0.1)", title="Time"),
            yaxis=dict(gridcolor="rgba(139,92,246,0.1)", title="Spam Probability", range=[0, 1]),
            margin=dict(t=20, b=40, l=60, r=20),
            height=350,
            showlegend=True,
        )
        st.plotly_chart(fig_timeline, use_container_width=True)


# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748b; font-size: 0.85rem;'>"
    "🛡️ Intelligent Social Media Spam Detection System — Built with Streamlit + scikit-learn"
    "</div>",
    unsafe_allow_html=True,
)
