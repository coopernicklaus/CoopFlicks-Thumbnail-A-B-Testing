"""
Author: Cooper Christensen
Date: 3/18/2026

"""

import pandas as pd
import numpy as np

# Makes results reproducible - same "random" data every time you run it
np.random.seed(42)

# --- Settings ---
NUM_USERS = 1000  # Total number of simulated users

# Click-through rates for each thumbnail
# Thumbnail B is slightly better - this is what our test should detect
CTR_A = 0.25  # 25% of users who see Thumbnail A will click
CTR_B = 0.32  # 32% of users who see Thumbnail B will click

# --- Assign users to groups ---
# Each user is randomly assigned to either group A or group B
groups = np.random.choice(['A', 'B'], size=NUM_USERS)

# --- Simulate clicks ---
# For each user, randomly determine if they clicked based on their group's CTR
clicks = []
for group in groups:
    if group == 'A':
        clicked = np.random.binomial(1, CTR_A)  # 1 = clicked, 0 = did not click
    else:
        clicked = np.random.binomial(1, CTR_B)
    clicks.append(clicked)

# --- Build the DataFrame ---
df = pd.DataFrame({
    'user_id': range(1, NUM_USERS + 1),
    'group': groups,       # 'A' = saw Thumbnail A, 'B' = saw Thumbnail B
    'clicked': clicks      # 1 = clicked, 0 = did not click
})

# --- Save to CSV ---
df.to_csv('data/ab_test_results.csv', index=False)

# --- Preview the data ---
print("Data generated successfully!")
print(f"Total users: {NUM_USERS}")
print(f"\nFirst 10 rows:")
print(df.head(10))
print(f"\nGroup breakdown:")
print(df.groupby('group')['clicked'].agg(['count', 'sum', 'mean']).rename(columns={
    'count': 'total_users',
    'sum': 'total_clicks',
    'mean': 'click_through_rate'
}))