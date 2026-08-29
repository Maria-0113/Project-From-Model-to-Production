import pandas as pd

def sample_transactions(n, min_fraud=1):
    X = pd.read_csv("data/splits/dataset_v1/X_test.csv")
    y = pd.read_csv("data/splits/dataset_v1/y_test.csv").iloc[:, 0]

    fraud = X[y == 1].sample(min_fraud)
    rest = X.drop(fraud.index).sample(n - min_fraud)

    idx = pd.concat([fraud, rest]).sample(frac=1).index  # shuffled row indices
    sample = X.loc[idx].copy()
    sample.to_csv("sample_for_prediction.csv", index=False)
    sample["true_label"] = y.loc[idx]  # keep ground truth alongside

    sample.to_csv("sample_with_labels.csv", index=False)
    return sample

if __name__ == "__main__":
    sample_transactions(10, min_fraud=3)
