from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import Session

from app.db.init_db import create_all
from app.models.ai_classification import AIClassificationRecord
from app.models.bitrix_entity import BitrixEntityRecord
from app.models.enums import RequestStatus
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.models.routing_decision import RoutingDecisionRecord


def test_create_all_builds_expected_tables():
    engine = create_engine("sqlite+pysqlite:///:memory:")

    create_all(engine)

    inspector = inspect(engine)
    assert set(inspector.get_table_names()) == {
        "ai_classifications",
        "bitrix_entities",
        "intake_requests",
        "processing_logs",
        "routing_decisions",
    }


def test_intake_request_defaults_to_received():
    engine = create_engine("sqlite+pysqlite:///:memory:")
    create_all(engine)

    record = IntakeRequestRecord(
        idempotency_key="demo-1",
        source="web_form",
        raw_payload_masked="{\"message\":\"masked\"}",
        raw_text="Hello there",
    )

    with Session(engine) as session:
        session.add(record)
        session.flush()
        session.refresh(record)

        assert record.status == RequestStatus.received
        assert record.retry_count == 0


def test_model_tables_are_exposed():
    assert IntakeRequestRecord.__tablename__ == "intake_requests"
    assert AIClassificationRecord.__tablename__ == "ai_classifications"
    assert RoutingDecisionRecord.__tablename__ == "routing_decisions"
    assert BitrixEntityRecord.__tablename__ == "bitrix_entities"
    assert ProcessingLogRecord.__tablename__ == "processing_logs"
