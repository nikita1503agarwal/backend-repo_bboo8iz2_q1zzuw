from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import os

from database import db, create_document, get_documents, database_url, database_name
from schemas import Contact as ContactSchema

app = FastAPI(title="Comphilfe API", version="1.0.0")

# CORS for local dev and hosted frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ContactRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=60)
    message: str = Field(..., min_length=5, max_length=5000)


@app.get("/")
async def root():
    return {"message": "Comphilfe API is running"}


@app.get("/test")
async def test():
    status = {
        "backend": "ok",
        "database": "disabled",
        "database_url": database_url or "",
        "database_name": database_name or "",
        "connection_status": "not configured",
        "collections": [],
    }
    try:
        if db is not None:
            status["database"] = "ok"
            status["connection_status"] = "connected"
            status["collections"] = sorted(db.list_collection_names())
        else:
            status["database"] = "not available"
            status["connection_status"] = "missing DATABASE_URL/NAME"
    except Exception as e:
        status["database"] = "error"
        status["connection_status"] = str(e)
    return status


@app.post("/contact")
async def submit_contact(payload: ContactRequest):
    try:
        # validate using schema and insert
        contact_doc = ContactSchema(
            name=payload.name,
            email=str(payload.email),
            phone=payload.phone,
            message=payload.message,
            source="website",
            status="new",
        )
        inserted_id = create_document("contact", contact_doc)
        return {"success": True, "id": inserted_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    return {"status": "ok"}
