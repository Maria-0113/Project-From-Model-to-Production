from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from pathlib import Path
import uuid
import joblib
from datetime import datetime
import os

import logging
logger = logging.getLogger(__name__)

def train_model(df, dataset_version):
    """
    Train an XGBoost classifier for fraud detection and persist it to disk.

    Splits the input DataFrame into train/test sets (80/20, stratified on
    the target), trains an XGBClassifier with class imbalance handled via
    `scale_pos_weight`, saves the fitted model as a .joblib file under
    './models/<uuid>.joblib', and evaluates it on the held-out test set.

    Args:
        df (pd.DataFrame): Input dataset containing a binary "Class" column
            (1 = fraud, 0 = normal) and all other columns as features.

    Returns:
        dict: {
            "id" (str): UUID identifying the saved model (matches the
                filename in the models directory),
            "trained_time" (str): ISO 8601 timestamp of when training finished,
            "precision" (float): Weighted-average precision on the test set,
            "recall" (float): Weighted-average recall on the test set,
            "f1" (float): Weighted-average F1 score on the test set,
            "auc" (float): ROC AUC score on the test set, based on predicted
                fraud probabilities,
        }

    Side effects:
        - Creates a "models/" directory in the current working directory
          if it doesn't already exist.
        - Writes the trained model to "models/<id>.joblib".
    """

    X = df.drop("Class", axis=1) #features
    y = df["Class"] #target

    logger.info(f"Splitting data into train/test sets (80/20, stratified on target)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    split_dir = f"data/splits/{dataset_version}"
    os.makedirs(split_dir, exist_ok=True)

    splits = {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }

    for name, data in splits.items():
        data.to_csv(f"{split_dir}/{name}.csv", index=False)

    fraud_count = sum(y_train == 1)
    normal_count = sum(y_train == 0)

    model = XGBClassifier(
        n_estimators=200, #number of trees
        max_depth=6, #maximum depth of each tree
        learning_rate=0.1, #speed; how much each new tree contributes
        subsample=0.8, #80% of rows per tree - less overfitting
        colsample_bytree=0.8, #80% of features per tree
        random_state=42,
        scale_pos_weight=normal_count / fraud_count, ##because the dataset is highly imbalanced
    )

    logger.info("Starting model training...")
    model.fit(X_train, y_train)
    trained_time = datetime.now().isoformat()
    model_id = str(uuid.uuid4())
    logger.info(f"Model training completed successfully.Model ID: {model_id}. Trained time: {trained_time}")

    #saving the trained model 

    logger.info("Saving the trained model to disk...")
    MODELS_DIR = Path("models")
    MODELS_DIR.mkdir(exist_ok=True)
    model_path = MODELS_DIR / f"{model_id}.joblib"
    joblib.dump(model, model_path)

  
    #evaluation

    logger.info("Evaluating model performance on the test set...")
    y_pred = model.predict(X_test)
    y_prob = model.predict_proba(X_test)[:, 1] ### to take fraud probabilities instead of class labels

    report = classification_report(y_test, y_pred, output_dict=True)
    precision = report["1"]["precision"]
    recall = report["1"]["recall"]
    f1 = report["1"]["f1-score"]
    auc = roc_auc_score(y_test, y_prob)
    pr_auc = average_precision_score(y_test, y_prob)


    logger.info(f"Model performance metrics:   Precision: {precision:.4f}   Recall: {recall:.4f}   F1-Score: {f1:.4f}   AUC: {auc:.4f}")
    return {
    "id": model_id,
    "trained_time": trained_time,
    "precision": precision,
    "recall": recall,
    "f1": f1, 
    "auc": auc, 
    "pr_auc": pr_auc
    }


