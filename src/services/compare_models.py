from .model_exists import model_exists
from .load_model import load_model
from sklearn.metrics import classification_report, roc_auc_score, average_precision_score
from.validate_csv import validate_csv
from database.define_tables import ModelDeployment
from fastapi import HTTPException

import logging
logger = logging.getLogger(__name__)


def compare_models(model_id, dataset_version, db):

    model_metadata = model_exists(model_id, db)  
    new_metrics = {
    "precision": round(model_metadata.precision, 4),
    "recall": round(model_metadata.recall, 4),
    "f1": round(model_metadata.f1, 4),
    "auc": round(model_metadata.auc, 4),
    "pr_auc": round(model_metadata.pr_auc, 4)
    }
    ##get the model_id that is active now (from the ModelDeployment table).
    try:  
        deployed_model_id = (
        db.query(ModelDeployment.model_id)
        .filter(ModelDeployment.is_active == True)
        .scalar()
        )
    except Exception as e:
        logger.error(f"Error occurred while getting the model ID from the database table ModelDeployment: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while getting the model ID from the database table ModelDeployment:{e}")
    ##load it 
    if deployed_model_id is None: return True, {}

    try: 
        logger.info("Loading the deployed_model")
        deployed_model = load_model(deployed_model_id)
    except Exception as e:
        logger.error(f"Error occurred while loading the deployed model: {e}")
        raise HTTPException(status_code=500, detail=f"Error occurred while loading the deployed model:{e}")
    
    
    ###evaluate currently deployed model on the new test set (from the new dataset version)
    logger.info(f"Evaluating the deployed model (model_id: {deployed_model_id}) on the new test set")
    ##Load the same test dataset for evaluation:
    split_dir = f"data/splits/{dataset_version}"
    X_test = validate_csv(f"{split_dir}/X_test.csv") 
    y_test = validate_csv(f"{split_dir}/y_test.csv")
    logger.info("Evaluating the old model performance on the new test set...")
    y_pred = deployed_model.predict(X_test)
    y_prob = deployed_model.predict_proba(X_test)[:, 1] ### to take fraud probabilities instead of class labels
    pr_auc = average_precision_score(y_test, y_prob)

    report = classification_report(y_test, y_pred, output_dict=True)
    old_metrics = {
    "precision": round(report["1"]["precision"], 4),
    "recall": round(report["1"]["recall"], 4),
    "f1": round(report["1"]["f1-score"], 4),
    "auc": round(roc_auc_score(y_test, y_prob), 4),
    "pr_auc": round(pr_auc, 4)
    }
    ##Compare the models 
    comparison = {}

    for metric in old_metrics.keys():
        comparison[metric] = {
            "old": old_metrics[metric],
            "new": new_metrics[metric],
            "difference": new_metrics[metric] - old_metrics[metric]
        }

    logger.info(f"Comparison of old and new model metrics: {comparison}")
    logger.info(f"Checking which model is better based on the comparison of metrics...")
    
    new_is_better = (
        # Primary objective
        new_metrics["recall"] > old_metrics["recall"]

        # Precision must not deteriorate too much
        and
        new_metrics["precision"] >= old_metrics["precision"] - 0.02

        # Overall ranking performance must not deteriorate too much
        and
        new_metrics["pr_auc"] >= old_metrics["pr_auc"] - 0.005
    )

    if new_is_better:
        logger.info("New model is better. Ready for deployment.")
    else:
        logger.info("New model rejected.")

    return new_is_better, comparison
