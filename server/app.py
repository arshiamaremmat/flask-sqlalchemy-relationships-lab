#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_migrate import Migrate

from models import db, Event, Session, Speaker, Bio

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

migrate = Migrate(app, db)
db.init_app(app)

# -----------------------------
# Routes
# -----------------------------

@app.route('/events')
def get_events():
    events = Event.query.all()
    data = [
        {
            "id": e.id,
            "name": e.name,
            "location": e.location,
        }
        for e in events
    ]
    return jsonify(data), 200


@app.route('/events/<int:id>/sessions')
def get_event_sessions(id):
    event = Event.query.get(id)
    if not event:
        return jsonify({"error": "Event not found"}), 404

    sessions = [
        {
            "id": s.id,
            "title": s.title,
            "start_time": s.start_time.isoformat() if s.start_time else None,
        }
        for s in event.sessions
    ]
    return jsonify(sessions), 200


@app.route('/speakers')
def get_speakers():
    speakers = Speaker.query.all()
    data = [{"id": sp.id, "name": sp.name} for sp in speakers]
    return jsonify(data), 200


@app.route('/speakers/<int:id>')
def get_speaker(id):
    sp = Speaker.query.get(id)
    if not sp:
        return jsonify({"error": "Speaker not found"}), 404

    bio_text = sp.bio.bio_text if sp.bio else "No bio available"
    data = {
        "id": sp.id,
        "name": sp.name,
        "bio_text": bio_text,
    }
    return jsonify(data), 200


@app.route('/sessions/<int:id>/speakers')
def get_session_speakers(id):
    sess = Session.query.get(id)
    if not sess:
        return jsonify({"error": "Session not found"}), 404

    data = []
    for sp in sess.speakers:
        data.append(
            {
                "id": sp.id,
                "name": sp.name,
                "bio_text": sp.bio.bio_text if sp.bio else "No bio available",
            }
        )
    return jsonify(data), 200


if __name__ == '__main__':
    app.run(port=5555, debug=True)
