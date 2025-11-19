import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from bson import ObjectId

from database import db, create_document, get_documents
from schemas import Event

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def read_root():
    return {"message": "Paris History API"}


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name if hasattr(db, 'name') else "Unknown"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    return response


# Request models
class EventCreate(Event):
    pass


@app.post("/api/events")
def create_event(event: EventCreate):
    try:
        event_id = create_document("event", event)
        return {"id": event_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events", response_model=List[Event])
def list_events(limit: int = 200, year_from: Optional[int] = None, year_to: Optional[int] = None):
    try:
        filt = {}
        if year_from is not None or year_to is not None:
            year_filter = {}
            if year_from is not None:
                year_filter["$gte"] = year_from
            if year_to is not None:
                year_filter["$lte"] = year_to
            filt["year"] = year_filter
        docs = get_documents("event", filt, limit)
        # Convert ObjectId/_id to none and shape to Event
        events: List[Event] = []
        for d in docs:
            d.pop("_id", None)
            # Ensure subtitles typed-correctly
            if "subtitles" in d and isinstance(d["subtitles"], list):
                d["subtitles"] = [
                    {"start": s.get("start", 0.0), "end": s.get("end", 0.0), "text": s.get("text", "")} for s in d["subtitles"]
                ]
            events.append(Event(**d))
        return events
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/events/seed")
def seed_sample_events():
    """Seed a few sample Paris events for demo purposes."""
    samples = [
        {
            "title": "Prise de la Bastille",
            "year": 1789,
            "date": "1789-07-14",
            "description": "La prise de la Bastille marque le début symbolique de la Révolution française.",
            "latitude": 48.853, "longitude": 2.369,
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/5/5d/Prise_de_la_Bastille.jpg"
            ],
            "audio_url": None,
            "subtitles": []
        },
        {
            "title": "Exposition Universelle",
            "year": 1889,
            "date": "1889-05-06",
            "description": "Inauguration de la tour Eiffel à l'occasion de l'Exposition universelle.",
            "latitude": 48.8584, "longitude": 2.2945,
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/a/a8/Tour_Eiffel_Wikimedia_Commons.jpg"
            ],
            "audio_url": None,
            "subtitles": []
        },
        {
            "title": "Lutèce gallo-romaine",
            "year": -300,
            "date": None,
            "description": "Aux origines, Lutèce se développe sur l'île de la Cité et la montagne Sainte-Geneviève.",
            "latitude": 48.8494, "longitude": 2.3470,
            "images": [
                "https://upload.wikimedia.org/wikipedia/commons/2/23/Paris_-_Thermes_de_Cluny.jpg"
            ],
            "audio_url": None,
            "subtitles": []
        }
    ]

    inserted = 0
    for s in samples:
        try:
            create_document("event", s)
            inserted += 1
        except Exception:
            pass
    return {"inserted": inserted}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
