import pandas as pd

df = pd.read_csv("data/creditcard.csv")

# Shape and basic info
print(f"Data shape:\n{df.shape}")

# First look at the data
print(f"Data head:\n{df.head()}")

# Summary stats (spot weird min/max, scale differences)
print(f"Data summary stats:\n{df.describe()}")

# How many duplicate rows exist
print(f"Number of duplicate rows: {df.duplicated().sum()}")

# Look at them before deleting, just to sanity-check
print(f"Duplicate rows:\n{df[df.duplicated(keep=False)]}")

df = df.drop_duplicates()

# Confirm
print(f"Number of duplicate rows after cleaning: {df.duplicated().sum()}")  # should be 0
print(f"Data shape after cleaning:\n{df.shape}")
df.to_csv('cleaned_data.csv', index=False)
print("Cleaned data saved to 'cleaned_data.csv'")
