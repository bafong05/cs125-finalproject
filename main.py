# main.py

import os
import mysql.connector
import redis
from datetime import datetime
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Body
from typing import Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter

# ====================================================================
#  SECRET LOADER
# ====================================================================
def load_secret(name):
    path = os.path.join("secrets", f"{name}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    raise Exception(f"Secret file {path} not found")


# ====================================================================
#  DATABASE INITIALIZATION
# ====================================================================
DB_USER = "root"
DB_PASS = load_secret("mysql_password")
DB_HOST = "mysql-cs125"
DB_NAME = "youth_group"

def mysql_connect():
    return mysql.connector.connect(
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        database=DB_NAME
    )

# MongoDB
mongo_client = MongoClient(
    load_secret("mongo_url"),
    tls=True,
    tlsAllowInvalidCertificates=True
)
mongo_db = mongo_client["youth_group"]

# Redis
redis_client = redis.Redis(
    host="redis-13814.c258.us-east-1-4.ec2.cloud.redislabs.com",
    port=13814,
    password=load_secret("redis_password"),
    decode_responses=True
)

# ====================================================================
#  FASTAPI SETUP
# ====================================================================
app = FastAPI(
    title="Youth Group API",
    description="Youth group system using MySQL + MongoDB + Redis."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,
)


# ====================================================================
#  HELPERS & CORE FUNCTIONS (USED BY REST + GRAPHQL)
# ====================================================================

def list_tables():
    db = mysql_connect()
    cur = db.cursor()
    cur.execute("SHOW TABLES;")
    tables = [t[0] for t in cur.fetchall()]
    cur.close()
    db.close()
    return tables


# --------------------------
# STUDENTS
# --------------------------
def get_all_students():
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                s.studentID, s.firstName, s.lastName, s.age,
                s.phoneNumber, s.email, s.groupID,
                g1.firstName AS g1_first, g1.lastName AS g1_last,
                g2.firstName AS g2_first, g2.lastName AS g2_last
            FROM Student s
            LEFT JOIN Guardian g1 ON s.guardian1ID = g1.guardianID
            LEFT JOIN Guardian g2 ON s.guardian2ID = g2.guardianID;
        """)
        rows = cursor.fetchall()
        cursor.close()
        db.close()

        students = []
        for r in rows:
            # Format guardians as strings (frontend expects array of strings)
            guardians = []
            if r["g1_first"]:
                guardians.append(f"{r['g1_first']} {r['g1_last']}")
            if r["g2_first"]:
                guardians.append(f"{r['g2_first']} {r['g2_last']}")

            students.append({
                "studentID": r["studentID"],
                "firstName": r["firstName"],
                "lastName": r["lastName"],
                "age": r["age"],
                "phoneNumber": r["phoneNumber"],
                "email": r["email"],
                "groupID": r["groupID"],
                "guardians": guardians,
            })

        return students

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



def get_student_by_id(student_id: int):
    db = mysql_connect()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT * FROM Student WHERE studentID=%s;", (student_id,))
    row = cur.fetchone()
    cur.close()
    db.close()

    if not row:
        raise HTTPException(status_code=404, detail="Student not found")

    return row



# --------------------------
# GROUPS
# --------------------------
def get_groups():
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)

    cursor.execute("SELECT groupID, name FROM SmallGroup;")
    groups = {
        g["groupID"]: {"groupID": g["groupID"], "name": g["name"], "members": [], "leaderNames": []}
        for g in cursor.fetchall()
    }

    cursor.execute("SELECT firstName, lastName, groupID FROM Leader;")
    for row in cursor.fetchall():
        groups[row["groupID"]]["leaderNames"].append(
            f"{row['firstName']} {row['lastName']}"
        )

    cursor.execute("SELECT * FROM Student;")
    for s in cursor.fetchall():
        groups[s["groupID"]]["members"].append(s)

    cursor.close()
    db.close()
    return list(groups.values())



# --------------------------
# EVENTS
# --------------------------
def create_event(event_data: dict):
    """
    Creates a new event in MySQL and stores customFields in MongoDB.
    event_data should contain: name, location, date, time, customFields (optional)
    """
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Insert into MySQL Event table
        cursor.execute("""
            INSERT INTO Event (name, location, date, time)
            VALUES (%s, %s, %s, %s)
        """, (
            event_data.get("name"),
            event_data.get("location"),
            event_data.get("date"),
            event_data.get("time")
        ))
        
        # Get the auto-generated eventID
        event_id = cursor.lastrowid
        db.commit()
        
        # Store customFields in MongoDB if provided
        custom_fields = event_data.get("customFields", {})
        if custom_fields:
            mongo_db["event_data"].insert_one({
                "eventID": event_id,
                "customFields": custom_fields
            })
        
        cursor.close()
        db.close()
        
        # Return the created event (fetch it to ensure consistency)
        return get_event_data(event_id)
        
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")


def get_all_events():
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("""
            SELECT eventID, name, location, date, CAST(time AS CHAR) AS time
            FROM Event ORDER BY date, time;
        """)
        events = cursor.fetchall()
        cursor.close()
        db.close()

        # Attach custom fields from Mongo
        for e in events:
            try:
                doc = mongo_db["event_data"].find_one({"eventID": e["eventID"]}, {"_id": 0})
                e["customFields"] = doc["customFields"] if doc else {}
            except Exception as mongo_err:
                print(f"MongoDB error for event {e['eventID']}: {mongo_err}")
                e["customFields"] = {}

        return events
    except Exception as e:
        print(f"Error in get_all_events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")



def get_event_data(event_id: int):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    cursor.execute("""
        SELECT eventID, name, location, date, CAST(time AS CHAR) AS time
        FROM Event WHERE eventID=%s;
    """, (event_id,))
    event = cursor.fetchone()
    cursor.close()
    db.close()

    if not event:
        raise HTTPException(status_code=404, detail="Event not found")

    doc = mongo_db["event_data"].find_one({"eventID": event_id}, {"_id": 0})
    event["customFields"] = doc["customFields"] if doc else {}

    return event


def update_event(event_id: int, event_data: dict):
    """
    Updates an existing event in MySQL and MongoDB.
    event_data should contain: name, location, date, time, customFields (optional)
    """
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Check if event exists
        cursor.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Update MySQL Event table
        cursor.execute("""
            UPDATE Event 
            SET name=%s, location=%s, date=%s, time=%s
            WHERE eventID=%s
        """, (
            event_data.get("name"),
            event_data.get("location"),
            event_data.get("date"),
            event_data.get("time"),
            event_id
        ))
        
        db.commit()
        
        # Update customFields in MongoDB
        custom_fields = event_data.get("customFields", {})
        existing_doc = mongo_db["event_data"].find_one({"eventID": event_id})
        
        if custom_fields:
            if existing_doc:
                # Update existing document
                mongo_db["event_data"].update_one(
                    {"eventID": event_id},
                    {"$set": {"customFields": custom_fields}}
                )
            else:
                # Create new document
                mongo_db["event_data"].insert_one({
                    "eventID": event_id,
                    "customFields": custom_fields
                })
        else:
            # Remove customFields if empty
            if existing_doc:
                mongo_db["event_data"].delete_one({"eventID": event_id})
        
        cursor.close()
        db.close()
        
        # Return the updated event
        return get_event_data(event_id)
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")


def delete_event(event_id: int):
    """
    Deletes an event from MySQL and MongoDB.
    Note: MySQL foreign key constraints will handle cascading deletes.
    """
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    
    try:
        # Check if event exists
        cursor.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        
        # Delete from MySQL (cascades to related tables)
        cursor.execute("DELETE FROM Event WHERE eventID=%s;", (event_id,))
        db.commit()
        
        # Delete from MongoDB
        mongo_db["event_data"].delete_many({"eventID": event_id})
        mongo_db["walk_ins"].delete_many({"eventID": event_id})
        
        cursor.close()
        db.close()
        
        return {"message": "Event deleted successfully", "eventID": event_id}
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to delete event: {str(e)}")



# --------------------------
# ATTENDANCE – REDIS SET
# --------------------------

CHECKED_IN_KEY = lambda eid: f"event:{eid}:checkedIn"
ATTENDEES_KEY = lambda eid: f"event:{eid}:attendees"  # Tracks all who checked in (even if checked out)

def check_in(event_id: int, student_id: int):

    # Validate IDs
    db = mysql_connect()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")

    cur.execute("SELECT studentID FROM Student WHERE studentID=%s;", (student_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Student not found")

    cur.close()
    db.close()

    # Redis SET add - add to both checkedIn (current) and attendees (all-time)
    redis_client.sadd(CHECKED_IN_KEY(event_id), str(student_id))
    redis_client.sadd(ATTENDEES_KEY(event_id), str(student_id))  # Track all attendees

    return {"message": "checked in", "eventID": event_id, "studentID": student_id}



def check_out(event_id: int, student_id: int):
    if not redis_client.sismember(CHECKED_IN_KEY(event_id), str(student_id)):
        raise HTTPException(status_code=400, detail="Student is not checked in")

    # Remove from checkedIn but keep in attendees (so they're still counted in total)
    redis_client.srem(CHECKED_IN_KEY(event_id), str(student_id))
    # Note: We DON'T remove from ATTENDEES_KEY - they still count as attendees

    return {"message": "checked out", "eventID": event_id, "studentID": student_id}



def live_attendance(event_id: int):
    raw = redis_client.smembers(CHECKED_IN_KEY(event_id))
    ids = sorted(int(x) for x in raw)

    # Fetch student names from MySQL
    checked_in_students = []
    if ids:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(
            f"SELECT studentID, firstName, lastName FROM Student WHERE studentID IN ({placeholders})",
            ids
        )
        students = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Create a map of studentID to name
        student_map = {s["studentID"]: f"{s['firstName']} {s['lastName']}" for s in students}
        
        # Build checkedInStudents array with both ID and name
        checked_in_students = [
            {
                "studentID": sid,
                "name": student_map.get(sid, f"Student {sid}")
            }
            for sid in ids
        ]

    return {
        "eventID": event_id,
        "checkedIn": ids,
        "count": len(ids),
        "checkedInStudents": checked_in_students
    }



# --------------------------
# FINALIZE EVENT
# --------------------------
def finalize_event(event_id: int):
    """
    Your chosen finalize_event:
    ✔ Uses Redis SET
    ✔ Saves registered → MySQL Attendance
    ✔ Saves walk-ins → MongoDB walk_ins
    ✔ Deletes old Attendance for re-finalization
    """

    db = mysql_connect()
    cur = db.cursor(dictionary=True)

    # Validate event
    cur.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")

    # Pull attendance from Redis - use ATTENDEES_KEY to get ALL who checked in (including those who checked out)
    redis_raw = redis_client.smembers(ATTENDEES_KEY(event_id))
    attendees = sorted(int(x) for x in redis_raw)

    # Clear previous finalization
    cur.execute("DELETE FROM Attendance WHERE eventID=%s;", (event_id,))
    mongo_db["walk_ins"].delete_many({"eventID": event_id})

    registered = []
    walk_ins = []
    
    # Deduplicate attendees set (in case of any duplicates)
    unique_attendees = sorted(set(attendees))

    for sid in unique_attendees:
        # Check if already exists to prevent duplicates
        cur.execute("SELECT 1 FROM Attendance WHERE studentID=%s AND eventID=%s;", (sid, event_id))
        already_registered = cur.fetchone()
        
        cur.execute("SELECT 1 FROM Registration WHERE studentID=%s AND eventID=%s;",
                    (sid, event_id))
        is_registered = cur.fetchone()

        if is_registered:
            if not already_registered:  # Only insert if not already there
                cur.execute(
                    "INSERT INTO Attendance (studentID, eventID, checkInTime) VALUES (%s, %s, NOW())",
                    (sid, event_id)
                )
            registered.append(sid)
        else:
            # Check if walk-in already exists in MongoDB
            existing_walkin = mongo_db["walk_ins"].find_one({"eventID": event_id, "studentID": sid})
            if not existing_walkin:  # Only insert if not already there
                mongo_db["walk_ins"].insert_one({
                    "eventID": event_id,
                    "studentID": sid,
                    "checkInTime": datetime.now()
                })
            walk_ins.append(sid)

    db.commit()
    cur.close()
    db.close()

    # Clear Redis keys
    redis_client.delete(CHECKED_IN_KEY(event_id))
    redis_client.delete(ATTENDEES_KEY(event_id))

    return {
        "message": "Event finalized successfully",
        "eventID": event_id,
        "registeredSaved": registered,
        "walkInsLogged": walk_ins,
        "totalRegistered": len(registered),
        "totalWalkIns": len(walk_ins),
        "totalAttendees": len(registered) + len(walk_ins)
    }



# --------------------------
# VIEW FINALIZED ATTENDANCE
# --------------------------
def get_finalized_attendance_view(event_id: int):
    # Check if event exists and get event date/time
    db = mysql_connect()
    cur = db.cursor(dictionary=True)
    
    cur.execute("SELECT eventID, name, date, time FROM Event WHERE eventID=%s;", (event_id,))
    event = cur.fetchone()
    
    if not event:
        cur.close()
        db.close()
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Load registered attendees from MySQL (deduplicate by studentID)
    cur.execute("""
        SELECT a.studentID, s.firstName, s.lastName
        FROM Attendance a
        JOIN Student s ON a.studentID = s.studentID
        WHERE eventID=%s
        GROUP BY a.studentID, s.firstName, s.lastName;
    """, (event_id,))
    registered = cur.fetchall()

    # Load walk-ins from MongoDB (deduplicate by studentID, keep earliest checkInTime)
    walkins_raw = list(mongo_db["walk_ins"].find({"eventID": event_id}, {"_id": 0}))
    
    # Deduplicate walk-ins by studentID, keeping the earliest checkInTime
    walkins_dict = {}
    for w in walkins_raw:
        student_id = w["studentID"]
        if student_id not in walkins_dict:
            walkins_dict[student_id] = w
        else:
            # Keep the one with earlier checkInTime
            existing_time = walkins_dict[student_id].get("checkInTime")
            new_time = w.get("checkInTime")
            if new_time and (not existing_time or new_time < existing_time):
                walkins_dict[student_id] = w
    
    walkin_ids = list(walkins_dict.keys())
    
    # Fetch student names for walk-ins
    walkin_students = {}
    if walkin_ids:
        placeholders = ','.join(['%s'] * len(walkin_ids))
        cur.execute(
            f"SELECT studentID, firstName, lastName FROM Student WHERE studentID IN ({placeholders})",
            walkin_ids
        )
        for row in cur.fetchall():
            walkin_students[row["studentID"]] = {
                "firstName": row["firstName"],
                "lastName": row["lastName"]
            }
    
    walkins_list = []
    for student_id, w in walkins_dict.items():
        student_info = walkin_students.get(student_id, {})
        walkins_list.append({
            "studentID": student_id,
            "firstName": student_info.get("firstName", "Unknown"),
            "lastName": student_info.get("lastName", ""),
            "isWalkIn": True
        })

    cur.close()
    db.close()
    
    # Check if event has been started (has any data in Redis or finalized data)
    # Check both checkedIn (current) and attendees (all-time) sets
    has_redis_data = redis_client.exists(CHECKED_IN_KEY(event_id)) or redis_client.exists(ATTENDEES_KEY(event_id))
    has_finalized_data = len(registered) > 0 or len(walkins_list) > 0
    
    # If no data at all (not started, not finalized), return "hasn't started" message
    if not has_redis_data and not has_finalized_data:
        return {
            "eventID": event_id,
            "status": "not_started",
            "message": "The event hasn't been started yet.",
            "registered": [],
            "walkIns": [],
            "totalRegistered": 0,
            "totalWalkIns": 0,
            "totalAttendees": 0,
            "hasFinalizedData": False
        }
    
    # If there's finalized data, return it
    if has_finalized_data:
        # Calculate counts from actual arrays (ensures accuracy)
        registered_count = len(registered) if registered else 0
        walkins_count = len(walkins_list) if walkins_list else 0
        total_count = registered_count + walkins_count
        
        return {
            "eventID": event_id,
            "status": "finalized",
            "message": "Finalized attendance data",
            "registered": registered,
            "walkIns": walkins_list,
            "totalRegistered": registered_count,
            "totalWalkIns": walkins_count,
            "totalAttendees": total_count,
            "hasFinalizedData": True
        }
    
    # If there's Redis data but not finalized yet
    return {
        "eventID": event_id,
        "status": "in_progress",
        "message": "Event is in progress. Finalize to view attendance data.",
        "registered": [],
        "walkIns": [],
        "totalRegistered": 0,
        "totalWalkIns": 0,
        "totalAttendees": 0,
        "hasFinalizedData": False
    }


# ====================================================================
# REST ROUTES
# ====================================================================

@app.get("/")
def root():
    return {"message": "Welcome to the Youth Group API!", "tables": list_tables()}


@app.get("/students")
def route_students():
    return get_all_students()


@app.get("/students/{student_id}")
def route_student(student_id: int):
    return get_student_by_id(student_id)


@app.get("/groups")
def route_groups():
    return get_groups()


@app.get("/events")
def route_events():
    return get_all_events()


@app.post("/events")
def route_create_event(event_data: dict = Body(...)):
    """
    Creates a new event.
    Expected body: { name, location, date, time, customFields (optional) }
    Note: eventID is auto-generated by MySQL, so it should not be included in the request.
    """
    # Remove eventID if provided (it will be auto-generated)
    if "eventID" in event_data:
        del event_data["eventID"]
    
    return create_event(event_data)


@app.api_route("/events/{event_id}", methods=["PUT"])
def route_update_event(event_id: int, event_data: Dict[str, Any] = Body(...)):
    """
    Updates an existing event.
    Expected body: { name, location, date, time, customFields (optional) }
    """
    return update_event(event_id, event_data)


@app.api_route("/events/{event_id}", methods=["DELETE"])
def route_delete_event(event_id: int):
    """
    Deletes an event.
    Note: This will cascade delete related records (registrations, attendance, etc.)
    """
    return delete_event(event_id)


@app.get("/events/{event_id}")
def route_event(event_id: int):
    return get_event_data(event_id)


@app.post("/events/{event_id}/checkin/{student_id}")
def route_checkin(event_id: int, student_id: int):
    return check_in(event_id, student_id)


@app.post("/events/{event_id}/checkout/{student_id}")
def route_checkout(event_id: int, student_id: int):
    return check_out(event_id, student_id)


@app.get("/events/{event_id}/live")
def route_live(event_id: int):
    return live_attendance(event_id)


@app.post("/events/{event_id}/finalize")
def route_finalize(event_id: int):
    return finalize_event(event_id)


@app.get("/events/{event_id}/finalized")
def route_finalized(event_id: int):
    return get_finalized_attendance_view(event_id)


@app.get("/events/{event_id}/attendance")
def route_attendance(event_id: int):
    """Alias for /finalized endpoint to match frontend expectations"""
    return get_finalized_attendance_view(event_id)


# ====================================================================
# GRAPHQL ROUTER — MUST BE LAST TO AVOID CIRCULAR IMPORT
# ====================================================================
from graphql_schema import schema

graphql_app = GraphQLRouter(schema, graphiql=True)
app.include_router(graphql_app, prefix="/graphql")
