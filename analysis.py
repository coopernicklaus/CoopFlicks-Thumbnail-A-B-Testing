"""
Author: Cooper Christensen
Date: 3/18/2026

"""

import pandas as pd
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns

# --- Load the data ---
df = pd.read_csv('data/ab_test_results.csv')

# --- Calculate click-through rates ---
summary = df.groupby('group')['clicked'].agg(['count', 'sum', 'mean']).rename(columns={
    'count': 'total_users',
    'sum': 'total_clicks',
    'mean': 'ctr'
})

ctr_a = summary.loc['A', 'ctr']
ctr_b = summary.loc['B', 'ctr']
users_a = summary.loc['A', 'total_users']
users_b = summary.loc['B', 'total_users']

print("=" * 45)
print("       CoopFlicks Thumbnail A/B Test")
print("=" * 45)
print(f"\nThumbnail A  →  CTR: {ctr_a:.2%}  |  Users: {users_a}")
print(f"Thumbnail B  →  CTR: {ctr_b:.2%}  |  Users: {users_b}")
print(f"\nLift (B over A): {((ctr_b - ctr_a) / ctr_a):.2%}")

# --- Chi-square test ---
# Build a contingency table: clicks vs non-clicks for each group
clicks_a = summary.loc['A', 'total_clicks']
clicks_b = summary.loc['B', 'total_clicks']
no_clicks_a = users_a - clicks_a
no_clicks_b = users_b - clicks_b

contingency_table = [[clicks_a, no_clicks_a],
                     [clicks_b, no_clicks_b]]

chi2, p_value, dof, expected = stats.chi2_contingency(contingency_table)

print(f"\n--- Statistical Test ---")
print(f"Chi-square statistic: {chi2:.4f}")
print(f"P-value:              {p_value:.4f}")
print(f"Degrees of freedom:   {dof}")

# --- Interpret the result ---
alpha = 0.05  # significance threshold
print(f"\n--- Result ---")
if p_value < alpha:
    print(f"✅ Statistically significant! (p={p_value:.4f} < {alpha})")
    print(f"   Thumbnail B outperforms Thumbnail A.")
    print(f"   Recommendation: Roll out Thumbnail B to all CoopFlicks users.")
else:
    print(f"❌ Not statistically significant (p={p_value:.4f} >= {alpha})")
    print(f"   We cannot confidently say one thumbnail is better.")
    print(f"   Recommendation: Run the test longer or with more users.")

# --- Confidence intervals ---
def confidence_interval(clicks, total, confidence=0.95):
    p = clicks / total
    z = stats.norm.ppf((1 + confidence) / 2)
    margin = z * np.sqrt((p * (1 - p)) / total)
    return p - margin, p + margin

ci_a = confidence_interval(clicks_a, users_a)
ci_b = confidence_interval(clicks_b, users_b)

print(f"\n--- 95% Confidence Intervals ---")
print(f"Thumbnail A: {ci_a[0]:.2%} to {ci_a[1]:.2%}")
print(f"Thumbnail B: {ci_b[0]:.2%} to {ci_b[1]:.2%}")

# --- Plot 1: CTR bar chart ---
plt.figure(figsize=(8, 5))
colors = ['#E50914', '#B20710']  # CoopFlicks red theme
bars = plt.bar(['Thumbnail A', 'Thumbnail B'], [ctr_a, ctr_b], color=colors, width=0.4)
plt.title('CoopFlicks Thumbnail A/B Test — Click-Through Rate', fontsize=14, fontweight='bold')
plt.ylabel('Click-Through Rate')
plt.ylim(0, max(ctr_a, ctr_b) * 1.4)

# Add CTR labels on top of bars
for bar, ctr in zip(bars, [ctr_a, ctr_b]):
    plt.text(bar.get_x() + bar.get_width() / 2,
             bar.get_height() + 0.005,
             f'{ctr:.2%}', ha='center', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('data/ctr_comparison.png', dpi=150)
plt.show()
print("\nChart saved to data/ctr_comparison.png")

# --- Plot 2: Confidence interval plot ---
plt.figure(figsize=(8, 5))
groups = ['Thumbnail A', 'Thumbnail B']
ctrs = [ctr_a, ctr_b]
errors = [(ctr_a - ci_a[0], ci_a[1] - ctr_a),
          (ctr_b - ci_b[0], ci_b[1] - ctr_b)]
yerr = np.array(errors).T

plt.errorbar(groups, ctrs, yerr=yerr, fmt='o', color='#E50914',
             ecolor='gray', elinewidth=2, capsize=10, markersize=10)
plt.title('CoopFlicks — CTR with 95% Confidence Intervals', fontsize=14, fontweight='bold')
plt.ylabel('Click-Through Rate')
plt.ylim(0, max(ctr_a, ctr_b) * 1.4)
plt.tight_layout()
plt.savefig('data/confidence_intervals.png', dpi=150)
plt.show()
print("Chart saved to data/confidence_intervals.png")