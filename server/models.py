from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

metadata = MetaData(
    naming_convention={
        "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
        "pk": "pk_%(table_name)s",
        "ix": "ix_%(table_name)s_%(column_0_name)s",
        "uq": "uq_%(table_name)s_%(column_0_name)s",
        "ck": "ck_%(table_name)s_%(constraint_name)s",
    }
)

db = SQLAlchemy(metadata=metadata)

# -----------------------------
# Association table (many-to-many: Session <-> Speaker)
# -----------------------------
session_speakers = db.Table(
    "session_speakers",
    db.Column("session_id", db.Integer, db.ForeignKey("sessions.id"), primary_key=True),
    db.Column("speaker_id", db.Integer, db.ForeignKey("speakers.id"), primary_key=True),
)

# -----------------------------
# Models
# -----------------------------
class Event(db.Model):
    __tablename__ = "events"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    location = db.Column(db.String, nullable=False)

    # One-to-Many: Event -> Sessions
    sessions = db.relationship(
        "Session",
        back_populates="event",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    def __repr__(self):
        return f"<Event id={self.id} name={self.name!r} location={self.location!r}>"


class Session(db.Model):
    __tablename__ = "sessions"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    start_time = db.Column(db.DateTime)
    event_id = db.Column(
        db.Integer,
        db.ForeignKey("events.id", ondelete="CASCADE"),
        nullable=False,
    )

    # backref to Event
    event = db.relationship("Event", back_populates="sessions")

    # Many-to-Many: Session <-> Speaker (through session_speakers)
    speakers = db.relationship(
        "Speaker",
        secondary=session_speakers,
        back_populates="sessions",
    )

    def __repr__(self):
        return f"<Session id={self.id} title={self.title!r} start_time={self.start_time!r}>"


class Speaker(db.Model):
    __tablename__ = "speakers"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)

    # One-to-One: Speaker -> Bio (delete bio when speaker deleted)
    bio = db.relationship(
        "Bio",
        back_populates="speaker",
        uselist=False,
        cascade="all, delete-orphan",
        passive_deletes=True,
    )

    # Many-to-Many: Speaker <-> Session
    sessions = db.relationship(
        "Session",
        secondary=session_speakers,
        back_populates="speakers",
    )

    def __repr__(self):
        return f"<Speaker id={self.id} name={self.name!r}>"


class Bio(db.Model):
    __tablename__ = "bios"

    id = db.Column(db.Integer, primary_key=True)
    bio_text = db.Column(db.Text, nullable=False)
    speaker_id = db.Column(
        db.Integer,
        db.ForeignKey("speakers.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    # backref to Speaker
    speaker = db.relationship("Speaker", back_populates="bio")

    def __repr__(self):
        return f"<Bio id={self.id} speaker_id={self.speaker_id} len(bio_text)={len(self.bio_text) if self.bio_text else 0}>"
