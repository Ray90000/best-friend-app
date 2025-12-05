from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import uuid

from models import Trip, Member, Transaction, SettlementResult
from logic import calculate_settlement
import database

app = FastAPI()

# Initialize Database
database.init_db()

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



@app.get("/trips", response_model=List[Trip])
def list_trips():
    return database.list_trips()

@app.post("/trips", response_model=Trip)
def create_trip(name: str):
    trip_id = str(uuid.uuid4())
    new_trip = Trip(id=trip_id, name=name)
    database.save_trip(new_trip)
    return new_trip

@app.patch("/trips/{trip_id}", response_model=Trip)
def update_trip_status(trip_id: str, status: str):
    trip = database.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    trip.status = status
    database.save_trip(trip)
    return trip

@app.delete("/trips/{trip_id}")
def delete_trip(trip_id: str):
    database.delete_trip(trip_id)
    return {"message": "Trip deleted"}

@app.get("/trips/{trip_id}", response_model=Trip)
def get_trip(trip_id: str):
    trip = database.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return trip

@app.post("/trips/{trip_id}/members", response_model=Trip)
def add_member(trip_id: str, member: Member):
    trip = database.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    if member.name in trip.members:
        raise HTTPException(status_code=400, detail="Member already exists")
    trip.members.append(member.name)
    database.save_trip(trip)
    return trip

@app.post("/trips/{trip_id}/transactions", response_model=Trip)
def add_transaction(trip_id: str, transaction: Transaction):
    trip = database.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    # Validate members
    if transaction.payer not in trip.members:
        raise HTTPException(status_code=400, detail=f"Payer {transaction.payer} not in trip")
    for m in transaction.for_whom:
        if m not in trip.members:
             raise HTTPException(status_code=400, detail=f"Member {m} not in trip")
             
    trip.transactions.append(transaction)
    database.save_trip(trip)
    return trip

@app.delete("/trips/{trip_id}/transactions/{transaction_id}", response_model=Trip)
def delete_transaction(trip_id: str, transaction_id: str):
    trip = database.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    # Filter out the transaction
    initial_len = len(trip.transactions)
    trip.transactions = [t for t in trip.transactions if t.id != transaction_id]
    
    if len(trip.transactions) == initial_len:
        raise HTTPException(status_code=404, detail="Transaction not found")
        
    database.save_trip(trip)
    return trip

@app.get("/trips/{trip_id}/settlement", response_model=SettlementResult)
def get_settlement(trip_id: str):
    trip = database.get_trip(trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    
    transfers = calculate_settlement(trip.transactions, trip.members)
    return SettlementResult(transfers=transfers)

# --- Static File Serving (for Production/Docker) ---
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Check if static folder exists (it will in Docker)
if os.path.exists("static"):
    # Mount assets (JS, CSS, Images)
    app.mount("/assets", StaticFiles(directory="static/assets"), name="assets")
    
    # Catch-all route for SPA (Vue Router)
    # This must be the LAST route defined
    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # Construct the full path
        file_path = f"static/{full_path}"
        
        # If it's a file and exists, serve it
        if os.path.isfile(file_path):
             return FileResponse(file_path)
             
        # Otherwise (directory, or doesn't exist), serve index.html
        return FileResponse("static/index.html")
