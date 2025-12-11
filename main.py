import sys
import os
import mysql.connector
import redis
from datetime import datetime
from contextlib import asynccontextmanager
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from typing import Optional, Dict, Any
from fastapi.middleware.cors import CORSMiddleware

# Guard to prevent circular import when GraphQL schema imports from main
GRAPHQL_IMPORT = "graphql_schema" in sys.modules

def load_secret(name):
    path = os.path.join("secrets", f"{name}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    raise Exception(f"Secret file {path} not found")

DB_USER = "root"
DB_PASS = load_secret("mysql_password")
DB_HOST = "mysql-cs125"
DB_NAME = "youth_group"

def mysql_connect():
    return mysql.connector.connect(
        user=DB_USER,
        password=DB_PASS,
        host=DB_HOST,
        database=DB_NAME)

mongo_client = None
mongo_db = None
redis_client = None

def get_mongo_db():
    """Get MongoDB database instance"""
    global mongo_db
    if mongo_db is None:
        raise RuntimeError("MongoDB not initialized. Call get_mongo_client() first.")
    return mongo_db

def get_redis_conn():
    """Get Redis connection"""
    global redis_client
    if redis_client is None:
        raise RuntimeError("Redis not initialized. Call get_redis_client() first.")
    return redis_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application startup and shutdown"""
    global mongo_client, mongo_db, redis_client
    print("Application startup: Initializing database connections...")
    
    mongo_client = MongoClient(
        load_secret("mongo_url"),
        tls=True,
        tlsAllowInvalidCertificates=True)
    mongo_db = mongo_client["youth_group"]

    redis_client = redis.Redis(
        host="redis-13814.c258.us-east-1-4.ec2.cloud.redislabs.com",
        port=13814,
        password=load_secret("redis_password"),
        decode_responses=True)
    print("Database connections initialized successfully.")
    yield
    print("Application shutdown: Closing database connections...")
    if mongo_client:
        mongo_client.close()
    if redis_client:
        redis_client.close()
    print("Database connections closed.")

app = FastAPI(
    title="Youth Group API",
    description="Youth group system using MySQL + MongoDB + Redis.",
    lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_headers=["*"],
    allow_methods=["*"],
    allow_credentials=True,)

def list_tables():
    db = mysql_connect()
    cur = db.cursor()
    cur.execute("SHOW TABLES;")
    tables = [t[0] for t in cur.fetchall()]
    cur.close()
    db.close()
    return tables

@app.get("/", response_class=FileResponse)
async def root():
    """
    Serves the main dashboard page.
    """
    index_path = os.path.join(os.path.dirname(__file__), "youth_group_frontend", "index.html")
    if os.path.exists(index_path):
        return index_path
    return {"message": "Welcome to the Youth Group API!", "tables": list_tables()}

# --------------------------
# STUDENTS
# --------------------------
@app.get("/students")
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
                "guardians": guardians,})
        return students
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/students/{student_id}")
def get_student_by_id(student_id: int):
    try:
        db = mysql_connect()
        cur = db.cursor(dictionary=True)
        cur.execute("SELECT * FROM Student WHERE studentID=%s;", (student_id,))
        row = cur.fetchone()
        cur.close()
        db.close()
        if not row:
            raise HTTPException(status_code=404, detail="Student not found")
        return row
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------
# GROUPS
# --------------------------
@app.get("/groups")
def get_groups():
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT groupID, name FROM SmallGroup;")
        groups = {
            g["groupID"]: {"groupID": g["groupID"], "name": g["name"], "members": [], "leaderNames": []}
            for g in cursor.fetchall()}
        cursor.execute("SELECT firstName, lastName, groupID FROM Leader;")
        for row in cursor.fetchall():
            groups[row["groupID"]]["leaderNames"].append(
                f"{row['firstName']} {row['lastName']}")
        cursor.execute("SELECT * FROM Student;")
        for s in cursor.fetchall():
            groups[s["groupID"]]["members"].append(s)
        cursor.close()
        db.close()
        return list(groups.values())
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --------------------------
# EVENTS
# --------------------------
@app.post("/events")
def create_event(event_data: dict = Body(...)):
    """Creates a new event. eventID is auto-generated."""
    if "eventID" in event_data:
        del event_data["eventID"]
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("""
            INSERT INTO Event (name, location, date, time)
            VALUES (%s, %s, %s, %s)
        """, (
            event_data.get("name"),
            event_data.get("location"),
            event_data.get("date"),
            event_data.get("time")))
        
        event_id = cursor.lastrowid
        db.commit()
        custom_fields = event_data.get("customFields", {})
        if custom_fields:
            try:
                mongo = get_mongo_db()
                mongo["event_data"].insert_one({
                    "eventID": event_id,
                    "customFields": custom_fields})
            except Exception as mongo_err:
                print(f"Warning: Failed to store customFields in MongoDB: {mongo_err}")
        cursor.close()
        db.close()
        return get_event_data(event_id)
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to create event: {str(e)}")

@app.get("/events")
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
        db = get_mongo_db()
        for e in events:
            try:
                doc = db["event_data"].find_one({"eventID": e["eventID"]}, {"_id": 0})
                e["customFields"] = doc["customFields"] if doc else {}
            except Exception as mongo_err:
                print(f"MongoDB error for event {e['eventID']}: {mongo_err}")
                e["customFields"] = {}
        return events
    except Exception as e:
        print(f"Error in get_all_events: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch events: {str(e)}")

@app.get("/events/{event_id}")
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
    db = get_mongo_db()
    doc = db["event_data"].find_one({"eventID": event_id}, {"_id": 0})
    event["customFields"] = doc["customFields"] if doc else {}
    return event

@app.api_route("/events/{event_id}", methods=["PUT"])
def update_event(event_id: int, event_data: Dict[str, Any] = Body(...)):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    
    try:
        cursor.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.execute("""
            UPDATE Event 
            SET name=%s, location=%s, date=%s, time=%s
            WHERE eventID=%s
        """, (
            event_data.get("name"),
            event_data.get("location"),
            event_data.get("date"),
            event_data.get("time"),
            event_id))
        db.commit()
        custom_fields = event_data.get("customFields", {})
        mongo = get_mongo_db()
        existing_doc = mongo["event_data"].find_one({"eventID": event_id})
        if custom_fields:
            if existing_doc:
                mongo["event_data"].update_one(
                    {"eventID": event_id},
                    {"$set": {"customFields": custom_fields}})
            else:
                mongo["event_data"].insert_one({
                    "eventID": event_id,
                    "customFields": custom_fields})
        else:
            if existing_doc:
                mongo["event_data"].delete_one({"eventID": event_id})
        cursor.close()
        db.close()
        return get_event_data(event_id)
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to update event: {str(e)}")

@app.api_route("/events/{event_id}", methods=["DELETE"])
def delete_event(event_id: int):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.execute("DELETE FROM Event WHERE eventID=%s;", (event_id,))
        db.commit()
        mongo = get_mongo_db()
        mongo["event_data"].delete_many({"eventID": event_id})
        mongo["walk_ins"].delete_many({"eventID": event_id})
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
# STUDENT ATTENDANCE HISTORY
# --------------------------
@app.get("/attendance/{student_id}")
def get_student_attendance_history(student_id: int):
    """Returns attendance history for a specific student"""
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT studentID FROM Student WHERE studentID=%s;", (student_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        cursor.execute("""
            SELECT 
                a.attendanceID,
                a.studentID,
                a.eventID,
                a.checkInTime,
                a.checkOutTime,
                e.name AS eventName,
                e.date,
                e.time AS eventTime,
                CASE WHEN r.studentID IS NOT NULL THEN 1 ELSE 0 END AS isRegistered
            FROM Attendance a
            JOIN Event e ON a.eventID = e.eventID
            LEFT JOIN Registration r ON a.studentID = r.studentID AND a.eventID = r.eventID
            WHERE a.studentID = %s
            ORDER BY e.date DESC, a.checkInTime DESC
        """, (student_id,))
        registered_records = cursor.fetchall()
        mongo = get_mongo_db()
        walk_ins = list(mongo["walk_ins"].find({"studentID": student_id}, {"_id": 0}))
        walk_in_event_ids = [w.get("eventID") for w in walk_ins if w.get("eventID")]
        walk_in_records = []
        if walk_in_event_ids:
            placeholders = ','.join(['%s'] * len(walk_in_event_ids))
            cursor.execute(f"""
                SELECT eventID, name, date, time
                FROM Event
                WHERE eventID IN ({placeholders})
            """, tuple(walk_in_event_ids))
            events_dict = {row["eventID"]: row for row in cursor.fetchall()}
            for walk_in in walk_ins:
                event_id = walk_in.get("eventID")
                if event_id in events_dict:
                    event = events_dict[event_id]
                    walk_in_records.append({
                        "eventID": event_id,
                        "eventName": event["name"],
                        "date": str(event["date"]),
                        "checkInTime": str(walk_in.get("checkInTime")) if walk_in.get("checkInTime") else None,
                        "checkOutTime": None,
                        "isRegistered": False,
                        "isWalkIn": True})
        cursor.close()
        db.close()
        attendance_history = []
        for record in registered_records:
            attendance_history.append({
                "eventName": record["eventName"],
                "date": str(record["date"]),
                "checkInTime": str(record["checkInTime"]) if record["checkInTime"] else None,
                "checkOutTime": str(record["checkOutTime"]) if record["checkOutTime"] else None,
                "isRegistered": bool(record["isRegistered"]),
                "isWalkIn": False})
        for record in walk_in_records:
            attendance_history.append({
                "eventName": record["eventName"],
                "date": record["date"],
                "checkInTime": record["checkInTime"],
                "checkOutTime": None,
                "isRegistered": False,
                "isWalkIn": True})
        attendance_history.sort(key=lambda x: (x["date"], x["checkInTime"] or ""), reverse=True)
        return attendance_history
    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to fetch attendance history: {str(e)}")

# -----------
# ATTENDANCE 
# -----------

CHECKED_IN_KEY = lambda eid: f"event:{eid}:checkedIn"
ATTENDEES_KEY = lambda eid: f"event:{eid}:attendees"

@app.post("/events/{event_id}/checkin/{student_id}")
def check_in(event_id: int, student_id: int):
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
    r = get_redis_conn()
    r.sadd(CHECKED_IN_KEY(event_id), str(student_id))
    r.sadd(ATTENDEES_KEY(event_id), str(student_id))
    return {"message": "checked in", "eventID": event_id, "studentID": student_id}

@app.post("/events/{event_id}/checkout/{student_id}")
def check_out(event_id: int, student_id: int):
    r = get_redis_conn()
    if not r.sismember(CHECKED_IN_KEY(event_id), str(student_id)):
        raise HTTPException(status_code=400, detail="Student is not checked in")
    r.srem(CHECKED_IN_KEY(event_id), str(student_id))
    return {"message": "checked out", "eventID": event_id, "studentID": student_id}

@app.get("/events/{event_id}/live")
def live_attendance(event_id: int):
    r = get_redis_conn()
    raw = r.smembers(CHECKED_IN_KEY(event_id))
    ids = sorted(int(x) for x in raw)
    checked_in_students = []
    if ids:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        placeholders = ','.join(['%s'] * len(ids))
        cursor.execute(f"SELECT studentID, firstName, lastName FROM Student WHERE studentID IN ({placeholders})",ids)
        students = cursor.fetchall()
        cursor.close()
        db.close()
        student_map = {s["studentID"]: f"{s['firstName']} {s['lastName']}" for s in students}
        checked_in_students = [{
                "studentID": sid,
                "name": student_map.get(sid, f"Student {sid}")
            }for sid in ids]
    return {
        "eventID": event_id,
        "checkedIn": ids,
        "count": len(ids),
        "checkedInStudents": checked_in_students}

# --------------------------
# FINALIZE EVENT
# --------------------------
@app.post("/events/{event_id}/finalize")
def finalize_event(event_id: int):
    db = mysql_connect()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
    if not cur.fetchone():
        raise HTTPException(status_code=404, detail="Event not found")
    r = get_redis_conn()
    redis_raw = r.smembers(ATTENDEES_KEY(event_id))
    attendees = sorted(int(x) for x in redis_raw)
    cur.execute("DELETE FROM Attendance WHERE eventID=%s;", (event_id,))
    mongo = get_mongo_db()
    mongo["walk_ins"].delete_many({"eventID": event_id})
    registered = []
    walk_ins = []
    unique_attendees = sorted(set(attendees))
    for sid in unique_attendees:
        cur.execute("SELECT 1 FROM Attendance WHERE studentID=%s AND eventID=%s;", (sid, event_id))
        already_registered = cur.fetchone()
        cur.execute("SELECT 1 FROM Registration WHERE studentID=%s AND eventID=%s;",
                    (sid, event_id))
        is_registered = cur.fetchone()
        if is_registered:
            if not already_registered:
                cur.execute(
                    "INSERT INTO Attendance (studentID, eventID, checkInTime) VALUES (%s, %s, NOW())",
                    (sid, event_id))
            registered.append(sid)
        else:
            existing_walkin = mongo["walk_ins"].find_one({"eventID": event_id, "studentID": sid})
            if not existing_walkin:
                mongo["walk_ins"].insert_one({
                    "eventID": event_id,
                    "studentID": sid,
                    "checkInTime": datetime.now()})
            walk_ins.append(sid)
    db.commit()
    cur.close()
    db.close()
    r = get_redis_conn()
    r.delete(CHECKED_IN_KEY(event_id))
    r.delete(ATTENDEES_KEY(event_id))
    return {
        "message": "Event finalized successfully",
        "eventID": event_id,
        "registeredSaved": registered,
        "walkInsLogged": walk_ins,
        "totalRegistered": len(registered),
        "totalWalkIns": len(walk_ins),
        "totalAttendees": len(registered) + len(walk_ins)}

# --------------------------
# VIEW FINALIZED ATTENDANCE
# --------------------------
@app.get("/events/{event_id}/finalized")
@app.get("/events/{event_id}/attendance")
def get_finalized_attendance_view(event_id: int):
    db = mysql_connect()
    cur = db.cursor(dictionary=True)
    cur.execute("SELECT eventID, name, date, time FROM Event WHERE eventID=%s;", (event_id,))
    event = cur.fetchone()
    if not event:
        cur.close()
        db.close()
        raise HTTPException(status_code=404, detail="Event not found")
    cur.execute("""
        SELECT a.studentID, s.firstName, s.lastName
        FROM Attendance a
        JOIN Student s ON a.studentID = s.studentID
        WHERE eventID=%s
        GROUP BY a.studentID, s.firstName, s.lastName;
    """, (event_id,))
    registered = cur.fetchall()
    mongo = get_mongo_db()
    walkins_raw = list(mongo["walk_ins"].find({"eventID": event_id}, {"_id": 0}))
    walkins_dict = {}
    for w in walkins_raw:
        student_id = w["studentID"]
        if student_id not in walkins_dict:
            walkins_dict[student_id] = w
        else:
            existing_time = walkins_dict[student_id].get("checkInTime")
            new_time = w.get("checkInTime")
            if new_time and (not existing_time or new_time < existing_time):
                walkins_dict[student_id] = w
    walkin_ids = list(walkins_dict.keys())
    walkin_students = {}
    if walkin_ids:
        placeholders = ','.join(['%s'] * len(walkin_ids))
        cur.execute(
            f"SELECT studentID, firstName, lastName FROM Student WHERE studentID IN ({placeholders})",
            walkin_ids)
        for row in cur.fetchall():
            walkin_students[row["studentID"]] = {
                "firstName": row["firstName"],
                "lastName": row["lastName"]}
    walkins_list = []
    for student_id, w in walkins_dict.items():
        student_info = walkin_students.get(student_id, {})
        walkins_list.append({
            "studentID": student_id,
            "firstName": student_info.get("firstName", "Unknown"),
            "lastName": student_info.get("lastName", ""),
            "isWalkIn": True})
    cur.close()
    db.close()
    r = get_redis_conn()
    has_redis_data = r.exists(CHECKED_IN_KEY(event_id)) or r.exists(ATTENDEES_KEY(event_id))
    has_finalized_data = len(registered) > 0 or len(walkins_list) > 0
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
            "hasFinalizedData": False}
    if has_finalized_data:
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
            "hasFinalizedData": True}
    return {
        "eventID": event_id,
        "status": "in_progress",
        "message": "Event is in progress. Finalize to view attendance data.",
        "registered": [],
        "walkIns": [],
        "totalRegistered": 0,
        "totalWalkIns": 0,
        "totalAttendees": 0,
        "hasFinalizedData": False}

# --------------------------
# STUDENT REGISTRATIONS
# --------------------------
@app.get("/students/{student_id}/registrations")
def get_student_registrations(student_id: int):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT studentID FROM Student WHERE studentID=%s;", (student_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        cursor.execute("""
            SELECT eventID 
            FROM Registration 
            WHERE studentID = %s
        """, (student_id,))
        registrations = cursor.fetchall()
        registered_event_ids = [r["eventID"] for r in registrations]
        cursor.close()
        db.close()
        return {"studentID": student_id, "registeredEvents": registered_event_ids}
    except HTTPException:
        raise
    except Exception as e:
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to fetch registrations: {str(e)}")

@app.post("/students/{student_id}/registrations/{event_id}")
def register_student(student_id: int, event_id: int):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT studentID FROM Student WHERE studentID=%s;", (student_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        cursor.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.execute("""
            SELECT 1 FROM Registration 
            WHERE studentID=%s AND eventID=%s
        """, (student_id, event_id))
        if cursor.fetchone():
            cursor.close()
            db.close()
            return {"message": "Student already registered for this event", "studentID": student_id, "eventID": event_id}
        cursor.execute("""
            INSERT INTO Registration (studentID, eventID)
            VALUES (%s, %s)
        """, (student_id, event_id))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "Student registered successfully", "studentID": student_id, "eventID": event_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to register student: {str(e)}")

@app.delete("/students/{student_id}/registrations/{event_id}")
def unregister_student(student_id: int, event_id: int):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT studentID FROM Student WHERE studentID=%s;", (student_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Student not found")
        cursor.execute("SELECT eventID FROM Event WHERE eventID=%s;", (event_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Event not found")
        cursor.execute("""
            SELECT 1 FROM Registration 
            WHERE studentID=%s AND eventID=%s
        """, (student_id, event_id))
        if not cursor.fetchone():
            cursor.close()
            db.close()
            return {"message": "Student not registered for this event", "studentID": student_id, "eventID": event_id}
        cursor.execute("""
            DELETE FROM Registration 
            WHERE studentID=%s AND eventID=%s
        """, (student_id, event_id))
        db.commit()
        cursor.close()
        db.close()
        return {"message": "Student unregistered successfully", "studentID": student_id, "eventID": event_id}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        cursor.close()
        db.close()
        raise HTTPException(status_code=500, detail=f"Failed to unregister student: {str(e)}")

# =================================
#  GRAPHQL ENDPOINT 
# =================================
# Lazy import to avoid circular dependency
def setup_graphql():
    from strawberry.fastapi import GraphQLRouter
    from graphql_schema import schema
    graphql_app = GraphQLRouter(schema, graphiql=True)
    app.include_router(graphql_app, prefix="/graphql")

setup_graphql()

@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Alias for root - serves the demo HTML page.
    """
    index_path = os.path.join(os.path.dirname(__file__), "youth_group_frontend", "index.html")
    if os.path.exists(index_path):
        return index_path
    return {"message": "Welcome to the Youth Group API!", "tables": list_tables()}

if __name__ == "__main__":
    print("\nTo run this FastAPI application:")
    print("1. pip install -r requirements.txt")
    print("2. cd youth_group_backend")
    print("3. uvicorn main:app --reload --port 8000")
    print("4. Visit http://127.0.0.1:8000/docs for REST API docs")
    print("5. Visit http://127.0.0.1:8000/demo for demo")
    print("6. Visit http://127.0.0.1:8000/graphql for GraphiQL")