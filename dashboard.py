"""
Author: Cooper Christensen
Date: 3/18/2026

"""

import streamlit as st
import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt

# --- Page config ---
st.set_page_config(
    page_title="CoopFlicks A/B Test Dashboard",
    page_icon="🎬",
    layout="wide"
)

# --- Header ---
st.title("🎬 CoopFlicks Thumbnail A/B Test Dashboard")
st.markdown("*Analyzing which thumbnail drives more clicks on the CoopFlicks platform*")
st.divider()

# --- Sidebar controls ---
st.sidebar.header("⚙️ Simulation Settings")
st.sidebar.markdown("Adjust settings to see how they affect the results")

num_users = st.sidebar.slider("Number of users", 100, 5000, 1000, step=100)
ctr_a = st.sidebar.slider("Thumbnail A click-through rate", 0.05, 0.60, 0.25, step=0.01, format="%.2f")
ctr_b = st.sidebar.slider("Thumbnail B click-through rate", 0.05, 0.60, 0.32, step=0.01, format="%.2f")
alpha = st.sidebar.selectbox("Significance level (alpha)", [0.01, 0.05, 0.10], index=1)

st.sidebar.divider()
st.sidebar.markdown("**What is alpha?**")
st.sidebar.markdown("Alpha is your threshold for declaring a winner. 0.05 means you accept a 5% chance the result is due to random chance.")

# --- Generate data based on sidebar inputs ---
np.random.seed(42)
groups = np.random.choice(['A', 'B'], size=num_users)
clicks = [np.random.binomial(1, ctr_a) if g == 'A' else np.random.binomial(1, ctr_b) for g in groups]
df = pd.DataFrame({'group': groups, 'clicked': clicks})

# --- Calculate stats ---
summary = df.groupby('group')['clicked'].agg(['count', 'sum', 'mean']).rename(columns={
    'count': 'total_users',
    'sum': 'total_clicks',
    'mean': 'ctr'
})

actual_ctr_a = summary.loc['A', 'ctr']
actual_ctr_b = summary.loc['B', 'ctr']
users_a = summary.loc['A', 'total_users']
users_b = summary.loc['B', 'total_users']
clicks_a = summary.loc['A', 'total_clicks']
clicks_b = summary.loc['B', 'total_clicks']
lift = ((actual_ctr_b - actual_ctr_a) / actual_ctr_a) * 100

# Chi-square test
contingency = [[clicks_a, users_a - clicks_a], [clicks_b, users_b - clicks_b]]
chi2, p_value, dof, _ = stats.chi2_contingency(contingency)

# Confidence intervals
def get_ci(clicks, total, confidence=0.95):
    p = clicks / total
    z = stats.norm.ppf((1 + confidence) / 2)
    margin = z * np.sqrt((p * (1 - p)) / total)
    return p - margin, p + margin

ci_a = get_ci(clicks_a, users_a)
ci_b = get_ci(clicks_b, users_b)

# --- Metric cards ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Thumbnail A CTR", f"{actual_ctr_a:.2%}")
col2.metric("Thumbnail B CTR", f"{actual_ctr_b:.2%}", delta=f"{lift:+.1f}% lift")
col3.metric("P-Value", f"{p_value:.4f}")
col4.metric("Total Users", f"{num_users:,}")

st.divider()

# --- Result banner ---
if p_value < alpha:
    st.success(f"✅ **Statistically significant result!** (p={p_value:.4f} < alpha={alpha})  \nThumbnail B outperforms Thumbnail A. **Recommendation: Roll out Thumbnail B to all CoopFlicks users.**")
else:
    st.warning(f"⚠️ **Not statistically significant** (p={p_value:.4f} >= alpha={alpha})  \nWe cannot confidently declare a winner yet. **Recommendation: Run the test longer or increase the number of users.**")

st.divider()

# --- Charts side by side ---
# --- Thumbnail display ---
st.subheader("🖼️ The Thumbnails Being Tested")
thumb_col1, thumb_col2 = st.columns(2)

with thumb_col1:
    st.markdown("**Thumbnail A**")
    st.image("images/thumbnail_a.jpg", use_container_width=True)
    st.caption(f"CTR: {actual_ctr_a:.2%}")

with thumb_col2:
    st.markdown("**Thumbnail B**")
    st.image("images/thumbnail_b.jpg", use_container_width=True)
    st.caption(f"CTR: {actual_ctr_b:.2%}")

st.divider()

# --- Charts side by side ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("Click-Through Rate Comparison")
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    colors = ['#E50914', '#B20710']
    bars = ax1.bar(['Thumbnail A', 'Thumbnail B'], [actual_ctr_a, actual_ctr_b], color=colors, width=0.4)
    ax1.set_ylabel('Click-Through Rate')
    ax1.set_ylim(0, max(actual_ctr_a, actual_ctr_b) * 1.4)
    ax1.set_title('CTR by Thumbnail', fontweight='bold')
    for bar, ctr in zip(bars, [actual_ctr_a, actual_ctr_b]):
        ax1.text(bar.get_x() + bar.get_width() / 2,
                 bar.get_height() + 0.005,
                 f'{ctr:.2%}', ha='center', fontsize=12, fontweight='bold')
    st.pyplot(fig1)

with col_right:
    st.subheader("95% Confidence Intervals")
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    ctrs = [actual_ctr_a, actual_ctr_b]
    errors = [(actual_ctr_a - ci_a[0], ci_a[1] - actual_ctr_a),
              (actual_ctr_b - ci_b[0], ci_b[1] - actual_ctr_b)]
    yerr = np.array(errors).T
    ax2.errorbar(['Thumbnail A', 'Thumbnail B'], ctrs, yerr=yerr,
                 fmt='o', color='#E50914', ecolor='gray',
                 elinewidth=2, capsize=10, markersize=10)
    ax2.set_ylabel('Click-Through Rate')
    ax2.set_ylim(0, max(actual_ctr_a, actual_ctr_b) * 1.4)
    ax2.set_title('CTR with 95% Confidence Intervals', fontweight='bold')
    st.pyplot(fig2)

st.divider()

# --- Winner announcement ---
st.subheader("🏆 And the winner is...")

if p_value < alpha:
    if actual_ctr_b > actual_ctr_a:
        st.markdown("### 🎉 Thumbnail B wins!")
        st.image("images/thumbnail_b.jpg", width=400)
        st.success(f"Thumbnail B had a **{actual_ctr_b:.2%} CTR** vs Thumbnail A's **{actual_ctr_a:.2%}** — a lift of **{lift:+.1f}%**. Roll it out to all CoopFlicks users!")
    else:
        st.markdown("### 🎉 Thumbnail A wins!")
        st.image("images/thumbnail_a.jpg", width=400)
        st.success(f"Thumbnail A had a **{actual_ctr_a:.2%} CTR** vs Thumbnail B's **{actual_ctr_b:.2%}** — a lift of **{abs(lift):.1f}%**. Roll it out to all CoopFlicks users!")
else:
    st.markdown("### 🤝 No winner yet!")
    thumb_col1, thumb_col2 = st.columns(2)
    with thumb_col1:
        st.image("images/thumbnail_a.jpg", use_container_width=True)
    with thumb_col2:
        st.image("images/thumbnail_b.jpg", use_container_width=True)
    st.warning("The test hasn't reached statistical significance yet. Keep collecting data before declaring a winner!")