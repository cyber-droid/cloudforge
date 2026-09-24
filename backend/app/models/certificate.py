"""
CloudForge Certificate Database Models.

Why this exists:
1. Formative Training Certificates: Issued by CloudForge upon verified completion of training curricula.
2. Secure Nonce & Verification Code: Cryptographically randomized verification tokens for public credential checking.
3. Immutability & Audit Trail: Snapshots recipient name and training title at the moment of issuance.
4. Idempotency: Unique constraint on (user_id, training_id) prevents race conditions and duplicates.
"""

import enum
import secrets
import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from app.models.certification import Certification, CertificationTraining
    from app.models.user import User

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TimestampMixin


class CertificateStatus(str, enum.Enum):
    """Lifecycle status of issued credential."""

    ISSUED = "issued"
    REVOKED = "revoked"


def generate_verification_code() -> str:
    """Generate cryptographically secure unguessable verification token."""
    return f"cf_vcode_{secrets.token_urlsafe(16)}"


def generate_certificate_number(prefix: str = "CF") -> str:
    """Generate formatted certificate serial number."""
    random_hex = secrets.token_hex(4).upper()
    return f"{prefix}-{random_hex}"


class Certificate(Base, TimestampMixin):
    """CloudForge-issued training completion certificate."""

    __tablename__ = "certificates"
    __table_args__ = (
        UniqueConstraint("user_id", "training_id", name="uq_user_training_certificate"),
    )

    id: Mapped[str] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
        index=True,
    )
    user_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    certification_id: Mapped[Optional[str]] = mapped_column(
        String(36),
        ForeignKey("certifications.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    training_id: Mapped[str] = mapped_column(
        String(36),
        ForeignKey("certification_trainings.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    certificate_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    verification_code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        default=generate_verification_code,
        nullable=False,
        index=True,
    )
    issued_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(30),
        default=CertificateStatus.ISSUED.value,
        nullable=False,
        index=True,
    )
    completion_percentage: Mapped[float] = mapped_column(
        Float,
        default=100.0,
        nullable=False,
    )
    recipient_name_snapshot: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    training_title_snapshot: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    # Relationships
    user: Mapped["User"] = relationship("User")
    certification: Mapped[Optional["Certification"]] = relationship("Certification")
    training: Mapped["CertificationTraining"] = relationship(
        "CertificationTraining", back_populates="certificates"
    )
