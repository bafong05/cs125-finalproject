import os
import mysql.connector
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Body

#MySQL Configuration
DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_NAME = "youth_group"

#MongoDB Configuration
mongo_client = MongoClient(
    os.getenv("MONGO_URL"),
    tls=True,
    tlsAllowInvalidCertificates=True
)
mongo_db = mongo_client["youth_group"]

app = FastAPI()

def mysql_connect():
    return mysql.connector.connect(
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    database=DB_NAME
    )

def list_tables():
    db = mysql_connect()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return tables

@app.get("/")
def root():
    return {
        "message": "Welcome to the Youth Group API!",
        "tables": list_tables()}

@app.get("/students")
def get_all_students():
    """
    Retrieves a list of all students from MySQL.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT studentID, firstName, lastName FROM Student ORDER BY firstName, lastName;")
        rows = cursor.fetchall()
        cursor.close()
        db.close()
        return rows
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    """
    Retrieves a specific student by their ID from MySQL.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT studentID, firstName, lastName FROM Student WHERE studentID = %s;", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        db.close()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@app.get("/events")
def get_all_events():
    """
    Retrieves a list of all events from MySQL.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT eventID, name, location, date, CAST(time AS CHAR) AS time FROM Event ORDER BY date, time;")
        events = cursor.fetchall()
        cursor.close()
        db.close()
        return events
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")

@app.post("/events")
def create_event(data: dict = Body(...)):
    """
    Adds a new event with custom fields to MongoDB.
    """
    if "eventID" not in data:
        raise HTTPException(status_code=400, detail="eventID is required")
    try:
        db = mysql_connect()
        cursor = db.cursor()
        cursor.execute("""
        INSERT INTO Event (eventID, name, location, date, time)
        VALUES (%s, %s, %s, %s, %s)
        """, (
        data["eventID"],
        data.get("name"),
        data.get("location"),
        data.get("date"),
        data.get("time")
        ))
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL insert failed: {e}")

    collection = mongo_db["event_data"]
    existing = collection.find_one({"eventID": data["eventID"]})
    if existing:
        raise HTTPException(status_code=400, detail="Event with this ID already exists")
    custom_doc = {
           "eventID": data["eventID"],
           "customFields": data.get("customFields", {})
       }
    collection.insert_one(custom_doc)
    return {
         "message": "Event successfully added",
         "eventID": data["eventID"],
         "customFields": custom_doc["customFields"]
    }

@app.get("/events/{event_id}")
def get_event_data(event_id: int):
    """
    Returns an event from MySQL and MongoDB.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
        SELECT eventID, name, location, date, CAST(time AS CHAR) AS time
        FROM Event
        WHERE eventID = %s;
        """, (event_id,))
        event_sql = cursor.fetchone()
        cursor.close()
        db.close()
        if not event_sql:
            raise HTTPException(status_code=404, detail="Event not found in MySQL")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL fetch failed: {e}")

    collection = mongo_db["event_data"]
    event_mongo = collection.find_one({"eventID": event_id}, {"_id": 0})
    if not event_mongo:
        return event_sql
    event_sql["customFields"] = event_mongo.get("customFields", {})
    return event_sql