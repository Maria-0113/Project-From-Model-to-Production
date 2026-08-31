from monthly_drift2 import create_monthly_drift
import pandas as pd

df = pd.read_csv("data/cleaned_data.csv")

monthly_data = {}

for month in range(1,13):

    monthly_data[f"month_{month}"] = create_monthly_drift(
        df,
        month
    )

for month, data in monthly_data.items():

    data.to_csv(
        f"data/{month}.csv",
        index=False
    )