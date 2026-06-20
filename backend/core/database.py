"""
core/database.py
SQLite persistence layer via SQLAlchemy. Manages token storage (single-row)
and snapshot history (one row per unique image_id).
"""
import json
import logging
import os
from contextlib import contextmanager
from typing import Generator, List, Optional
from sqlalchemy import create_engine, select, func
from sqlalchemy.orm import Session, sessionmaker
from core.orm_models import Base, Token, Snapshot

logger = logging.getLogger(__name__)

DB_PATH: str = os.getenv("DB_PATH", "teracyte.db")
DATABASE_URL: str = f"sqlite:///{DB_PATH}"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}, # safe for Flask threading
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)

def init_db() -> None:
    """Create all tables from ORM models and seed the single tokens row."""
    Base.metadata.create_all(engine)

    with SessionLocal() as session:
        #? We're using a single session row since only 1 user is expected; this simplifies token management
        existing = session.get(Token, 1)
        if not existing:
            session.add(Token(id=1, access=None, refresh=None))
            session.commit()

    logger.info(f"Database initialised at {DB_PATH}")


@contextmanager
def get_session() -> Generator[Session, None, None]:
    """Gets a session, tries to commit the transaction, and rolls back on error."""
    session = SessionLocal()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()

#* Token helpers *#

def save_tokens(access: str, refresh: str) -> None:
    with get_session() as session:
        token = session.get(Token, 1)
        token.access = access
        token.refresh = refresh

def get_tokens() -> tuple[Optional[str], Optional[str]]:
    with get_session() as session:
        token = session.get(Token, 1)
        if token:
            return token.access, token.refresh
    return None, None

def clear_tokens() -> None:
    with get_session() as session:
        token = session.get(Token, 1)
        if token:
            token.access = None
            token.refresh = None

#* Snapshot helpers *#

def insert_snapshot(
    image_id: str,
    timestamp: str,
    intensity_average: float,
    focus_score: float,
    classification_label: str,
    histogram: list,
    image_data_base64: str,
    processed_data_base64: Optional[str] = None,
) -> None:
    histogram_json = json.dumps(histogram)
    with get_session() as session:
        session.add(Snapshot(
            image_id=image_id,
            timestamp=timestamp,
            intensity_average=intensity_average,
            focus_score=focus_score,
            classification_label=classification_label,
            histogram_json=histogram_json,
            image_data_base64=image_data_base64,
            processed_data_base64=processed_data_base64,
        ))

def get_latest_image_id() -> Optional[str]:
    with get_session() as session:
        result = session.scalar(
            select(Snapshot.image_id)
            .order_by(Snapshot.timestamp.desc())
            .limit(1)
        )
    return result

# def get_snapshot(image_id: str) -> Optional[Snapshot]:
#     with get_session() as session:
#         return session.scalar(
#             select(Snapshot).where(Snapshot.image_id == image_id)
#         )

def get_history(limit: int = 50) -> List[Snapshot]:
    with get_session() as session:
        return list(session.scalars(
            select(Snapshot)
            .order_by(Snapshot.timestamp.desc())
            .limit(limit)
        ))

def get_stats() -> dict:
    with get_session() as session:
        total, avg_intensity, avg_focus = session.execute(
            select(
                func.count(Snapshot.id),
                func.avg(Snapshot.intensity_average),
                func.avg(Snapshot.focus_score),
            )
        ).one()

        label_rows = session.execute(
            select(Snapshot.classification_label, func.count(Snapshot.id))
            .group_by(Snapshot.classification_label)
        ).all()

    return {
        "total_snapshots": total or 0,
        "avg_intensity":   round(avg_intensity or 0, 2),
        "avg_focus":       round(avg_focus or 0, 4),
        "label_counts":    {label: cnt for label, cnt in label_rows},
    }
