"""Seed synthetic demo intake requests into a local SQLite database."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from sqlalchemy import select

from app.config import Settings
from app.db.init_db import create_all
from app.db.session import create_engine_from_settings, create_session_factory
from app.models.enums import RequestStatus
from app.models.intake_request import IntakeRequestRecord
from app.models.processing_log import ProcessingLogRecord
from app.schemas.intake import IntakeRequestCreate

DEFAULT_INPUT_PATH = ROOT_DIR / "demo_data" / "sample_requests.json"

SENSITIVE_FIELDS = {"email", "phone", "name", "company", "message"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Seed synthetic AI Lead Intake demo requests into a local database.",
    )
    parser.add_argument(
        "--database-url",
        default="sqlite+pysqlite:///./demo.sqlite3",
        help="SQLAlchemy database URL. Default: sqlite+pysqlite:///./demo.sqlite3",
    )
    parser.add_argument(
        "--input",
        default=str(DEFAULT_INPUT_PATH),
        help=f"Path to sample JSON input. Default: {DEFAULT_INPUT_PATH}",
    )
    parser.add_argument(
        "--replace",
        action="store_true",
        help="Delete existing intake requests before seeding.",
    )
    return parser.parse_args()


def normalize_database_url(database_url: str) -> str:
    sqlite_prefix = "sqlite+pysqlite:///"
    if not database_url.startswith(sqlite_prefix):
        return database_url

    raw_path = database_url.removeprefix(sqlite_prefix)
    if raw_path == ":memory:":
        return database_url

    resolved_path = Path(raw_path)
    if not resolved_path.is_absolute():
        resolved_path = (ROOT_DIR / resolved_path).resolve()

    return f"{sqlite_prefix}{resolved_path.as_posix()}"


def load_requests(input_path: Path) -> list[IntakeRequestCreate]:
    payload = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(payload, list):
        msg = "Sample request file must contain a JSON array."
        raise ValueError(msg)
    return [IntakeRequestCreate.model_validate(item) for item in payload]


def mask_payload(payload: IntakeRequestCreate) -> str:
    raw_data = payload.model_dump(mode="json")
    masked = {
        key: ("[masked]" if key in SENSITIVE_FIELDS and value is not None else value)
        for key, value in raw_data.items()
    }
    return json.dumps(masked, ensure_ascii=False, separators=(",", ":"))


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).resolve()
    requests = load_requests(input_path)

    settings = Settings(
        database_url=normalize_database_url(args.database_url),
        worker_autostart=False,
    )
    engine = create_engine_from_settings(settings)
    create_all(engine)
    session_factory = create_session_factory(engine)

    seeded = 0
    skipped = 0
    removed = 0

    with session_factory() as session:
        if args.replace:
            removed = session.query(ProcessingLogRecord).delete()
            removed_requests = session.query(IntakeRequestRecord).delete()
            removed += removed_requests
            session.commit()

        for payload in requests:
            existing = session.scalar(
                select(IntakeRequestRecord).where(
                    IntakeRequestRecord.idempotency_key == payload.idempotency_key
                )
            )
            if existing is not None:
                skipped += 1
                continue

            record = IntakeRequestRecord(
                idempotency_key=payload.idempotency_key,
                source=payload.source,
                raw_payload_masked=mask_payload(payload),
                raw_text=payload.message.strip(),
                status=RequestStatus.received,
            )
            session.add(record)
            session.flush()

            session.add(
                ProcessingLogRecord(
                    intake_id=record.id,
                    event="demo_seeded",
                    status=RequestStatus.received,
                    details=json.dumps(
                        {
                            "source": payload.source,
                            "idempotency_key": payload.idempotency_key,
                            "seed_input": str(input_path),
                        },
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ),
                )
            )
            seeded += 1

        session.commit()

    print(
        "Seed complete: "
        f"seeded={seeded} skipped={skipped} removed={removed} "
        f"database_url={settings.database_url}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
