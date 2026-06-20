"""
core/orm_models.py
SQLAlchemy ORM models. All models share a single Base so their tables
are registered in one metadata registry (required for create_all to work).
"""
from datetime import datetime, timezone
from sqlalchemy import Integer, String, Float, Text, CheckConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    pass

class Token(Base):
    """Single-row table (id always = 1) that holds the current JWT pair"""
    __tablename__ = "tokens"
    __table_args__ = (CheckConstraint("id = 1", name="single_row"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    access: Mapped[str | None] = mapped_column(Text, nullable=True)
    refresh: Mapped[str | None] = mapped_column(Text, nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Token updated_at={self.updated_at}>"


class Snapshot(Base):
    """
    One row per unique image_id captured from the microscope
    Stores raw metrics, both base64 image variants, and the histogram
    """
    __tablename__ = "snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    image_id: Mapped[str] = mapped_column(String(64), unique=True, nullable=False, index=True)
    timestamp: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    intensity_average: Mapped[float | None] = mapped_column(Float)
    focus_score: Mapped[float | None] = mapped_column(Float)
    classification_label: Mapped[str | None] = mapped_column(String(64))
    histogram_json: Mapped[str | None] = mapped_column(Text)           # JSON int[256]
    image_data_base64: Mapped[str | None] = mapped_column(Text)        # original PNG
    processed_data_base64: Mapped[str | None] = mapped_column(Text)    # Canny edge PNG
    created_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
    )

    def __repr__(self) -> str:
        return f"<Snapshot image_id={self.image_id} label={self.classification_label}>"
