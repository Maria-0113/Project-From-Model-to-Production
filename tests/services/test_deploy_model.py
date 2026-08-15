import pytest
from fastapi import HTTPException

from services.deploy_model import deploy_model
from database.define_tables import ModelDeployment


def test_deploying_unknown_model_raises_404(db_session):
    with pytest.raises(HTTPException) as exc_info:
        deploy_model("no-such-model", db_session)

    assert exc_info.value.status_code == 404


def test_deploying_a_model_creates_active_deployment(db_session, make_model_metadata):
    make_model_metadata(model_id="model-1")

    result = deploy_model("model-1", db_session)

    assert result.model_id == "model-1"
    assert result.is_active is True


def test_deploying_new_model_deactivates_previous_one(db_session, make_model_metadata, make_deployment):
    make_model_metadata(model_id="model-1")
    make_model_metadata(model_id="model-2")
    make_deployment(model_id="model-1", is_active=True)

    deploy_model("model-2", db_session)

    deployments = db_session.query(ModelDeployment).all()
    active = [d for d in deployments if d.is_active]
    assert len(active) == 1
    assert active[0].model_id == "model-2"


def test_only_one_active_deployment_after_multiple_deploys(db_session, make_model_metadata):
    for i in range(3):
        make_model_metadata(model_id=f"model-{i}")

    deploy_model("model-0", db_session)
    deploy_model("model-1", db_session)
    deploy_model("model-2", db_session)

    active = db_session.query(ModelDeployment).filter_by(is_active=True).all()
    assert len(active) == 1
    assert active[0].model_id == "model-2"
