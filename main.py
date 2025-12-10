import os
import mysql.connector
import redis
from datetime import datetime
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware


def load_secret(name):
    path = os.path.join("secrets", f"{name}.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            return f.read().strip()
    raise Exception(f"Secret file {path} not found")


# MySQL
DB_USER = "root"
DB_PASS = load_secret("mysql_password")
DB_HOST = "mysql-cs125"
DB_NAME = "youth_group"

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

app = FastAPI(
    title="Youth Management API",
    description="An API for interacting with the youth group, now using MySQL, MongoDB, and Redis."
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        query = """
                SELECT s.studentID, \
                       s.firstName, \
                       s.lastName, \
                       s.age, \
                       s.phoneNumber, \
                       s.email, \
                       s.groupID, \
                       g1.firstName AS g1_first, \
                       g1.lastName  AS g1_last, \
                       g2.firstName AS g2_first, \
                       g2.lastName  AS g2_last
                FROM Student s
                         LEFT JOIN Guardian g1 ON s.guardian1ID = g1.guardianID
                         LEFT JOIN Guardian g2 ON s.guardian2ID = g2.guardianID; \
                """
        cursor.execute(query)
        rows = cursor.fetchall()

        students = []
        for row in rows:
            guardians = []
            if row["g1_first"]:
                guardians.append(f"{row['g1_first']} {row['g1_last']}")
            if row["g2_first"]:
                guardians.append(f"{row['g2_first']} {row['g2_last']}")
            students.append({
                "studentID": row["studentID"],
                "firstName": row["firstName"],
                "lastName": row["lastName"],
                "age": row["age"],
                "phoneNumber": row["phoneNumber"],
                "email": row["email"],
                "groupID": row["groupID"],
                "guardians": guardians
            })
        cursor.close()
        db.close()
        return students
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
        cursor.execute("SELECT * FROM Student WHERE studentID = %s;", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        db.close()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")


@app.get("/groups")
def get_groups():
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)

    # 1. Get all groups
    cursor.execute("SELECT groupID, name FROM SmallGroup;")
    groups = {
        g["groupID"]: {
            "groupID": g["groupID"],
            "name": g["name"],
            "leaderNames": [],
            "members": []
        }
        for g in cursor.fetchall()
    }

    # 2. Attach leaders
    cursor.execute("""
        SELECT 
            leaderID,
            firstName,
            lastName,
            groupID
        FROM Leader;
    """)

    for l in cursor.fetchall():
        gid = l["groupID"]
        if gid in groups:
            fullname = f"{l['firstName']} {l['lastName']}"
            groups[gid]["leaderNames"].append(fullname)

    # 3. Attach members (full objects)
    cursor.execute("""
        SELECT 
            studentID,
            firstName,
            lastName,
            age,
            phoneNumber,
            email,
            guardian1ID,
            guardian2ID,
            groupID
        FROM Student;
    """)

    for s in cursor.fetchall():
        gid = s["groupID"]
        if gid in groups:
            groups[gid]["members"].append(s)

    return list(groups.values())


    # 2. Load leaders and attach to groups
    cursor.execute("""
        SELECT 
            firstName,
            lastName,
            groupID
        FROM Leader;
    """)

    for l in cursor.fetchall():
        gid = l["groupID"]
        if gid in groups:
            full = f"{l['firstName']} {l['lastName']}"
            groups[gid]["leaderNames"].append(full)

    return list(groups.values())



@app.get("/events")
def get_all_events():
    """
    Retrieves a list of all events from MySQL and MongoDB.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT eventID, name, location, date, CAST(time AS CHAR) AS time FROM Event ORDER BY date, time;")
        events = cursor.fetchall()
        cursor.close()
        db.close()
        
        # Fetch customFields from MongoDB for each event
        # First, check what's actually in MongoDB
        all_mongo_docs = list(mongo_db["event_data"].find({}, {"_id": 0}))
        print(f"DEBUG: Total documents in MongoDB event_data collection: {len(all_mongo_docs)}")
        if all_mongo_docs:
            print(f"DEBUG: Sample MongoDB document: {all_mongo_docs[0]}")
            print(f"DEBUG: All eventIDs in MongoDB: {[doc.get('eventID') for doc in all_mongo_docs]}")
            print(f"DEBUG: Types of eventIDs in MongoDB: {[type(doc.get('eventID')) for doc in all_mongo_docs[:3]]}")
        
        for event in events:
            event_id = event["eventID"]
            event_id_int = int(event_id)
            
            # Try querying with integer
            mongo_doc = mongo_db["event_data"].find_one(
                {"eventID": event_id_int},
                {"_id": 0}
            )
            
            # If not found, try with the original type
            if not mongo_doc:
                mongo_doc = mongo_db["event_data"].find_one(
                    {"eventID": event_id},
                    {"_id": 0}
                )
            
            if mongo_doc:
                event["customFields"] = mongo_doc.get("customFields", {})
                print(f"DEBUG: Found customFields for event {event_id}: {list(event['customFields'].keys())}")
            else:
                event["customFields"] = {}
                print(f"DEBUG: No customFields found for event {event_id} (searched as int: {event_id_int}, type: {type(event_id)})")
        
        return events
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")


@app.post("/events")
def create_event(data: dict = Body(...)):
    """
    Adds a new event (auto-generated eventID) to MySQL,
    then stores custom fields in MongoDB.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Event (name, location, date, time) VALUES (%s, %s, %s, %s)",
            (data.get("name"), data.get("location"), data.get("date"), data.get("time")
             ))
        new_event_id = cursor.lastrowid
        db.commit()
        cursor.close()
        db.close()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL insert failed: {e}")

        mongo_doc = {
            "eventID": event_id,
            "customFields": data.get("customFields", {})
        }
        mongo_db["event_data"].insert_one(mongo_doc)

        return {
            "message": "Event created",
            "eventID": event_id,
            "customFields": mongo_doc["customFields"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create event: {e}")


@app.get("/events/{event_id}")
def get_event_data(event_id: int):
    """
    Returns an event from MySQL and MongoDB.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT eventID, name, location, date, CAST(time AS CHAR) AS time FROM Event WHERE eventID = %s;",
            (event_id,))
        event_sql = cursor.fetchone()
        cursor.close()
        db.close()
        if not event_sql:
            raise HTTPException(status_code=404, detail="Event not found in MySQL")

        mongo_doc = mongo_db["event_data"].find_one(
            {"eventID": event_id},
            {"_id": 0}
        )
        if mongo_doc:
            event_sql["customFields"] = mongo_doc.get("customFields", {})

        return event_sql

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MySQL error: {e}")


@app.post("/events/{event_id}/checkin/{student_id}")
def check_in(event_id: int, student_id: int):
    """
    Check a student in with Redis
    Validates that both the event and student exist before checking in.
    """
    try:
        # Validate event exists
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT eventID FROM Event WHERE eventID = %s;", (event_id,))
        event = cursor.fetchone()
        
        # Validate student exists
        cursor.execute("SELECT studentID FROM Student WHERE studentID = %s;", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        # Check in with Redis (store as string for consistency)
        redis_client.sadd(f"event:{event_id}:checkedIn", str(student_id))
        redis_client.sadd(f"event:{event_id}:attendees", str(student_id))
        return {"message": "checked in", "eventID": event_id, "studentID": student_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check-in failed: {str(e)}")


@app.post("/events/{event_id}/checkout/{student_id}")
def check_out(event_id: int, student_id: int):
    """
    Check a student out with Redis
    Validates that both the event and student exist before checking out.
    """
    try:
        # Validate event exists
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT eventID FROM Event WHERE eventID = %s;", (event_id,))
        event = cursor.fetchone()
        
        # Validate student exists
        cursor.execute("SELECT studentID FROM Student WHERE studentID = %s;", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        db.close()
        
        if not event:
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        if not student:
            raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
        
        # Check if student is checked in
        # Redis stores values as strings, so we need to check both string and int formats
        is_checked_in = redis_client.sismember(f"event:{event_id}:checkedIn", str(student_id))
        if not is_checked_in:
            # Also try checking with integer in case it was stored differently
            is_checked_in = redis_client.sismember(f"event:{event_id}:checkedIn", student_id)
        
        if not is_checked_in:
            raise HTTPException(status_code=400, detail=f"Student {student_id} is not checked in")
        
        # Check out with Redis (remove as string for consistency)
        redis_client.srem(f"event:{event_id}:checkedIn", str(student_id))
        return {"message": "checked out", "eventID": event_id, "studentID": student_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Check-out failed: {str(e)}")


@app.get("/events/{event_id}/live")
def live_attendance(event_id: int):
    """
    Returns the live attendance of an event with Redis
    Includes student IDs and names of checked-in students
    """
    key = f"event:{event_id}:checkedIn"
    student_ids = [int(s.decode()) if isinstance(s, bytes) else int(s) for s in redis_client.smembers(key)]
    
    # Get student names from MySQL
    student_names = []
    if student_ids:
        try:
            db = mysql_connect()
            cursor = db.cursor(dictionary=True)
            # Create placeholders for IN clause
            placeholders = ','.join(['%s'] * len(student_ids))
            cursor.execute(
                f"SELECT studentID, firstName, lastName FROM Student WHERE studentID IN ({placeholders})",
                student_ids
            )
            students = cursor.fetchall()
            cursor.close()
            db.close()
            
            # Create a map of studentID to full name
            student_map = {s["studentID"]: f"{s['firstName']} {s['lastName']}" for s in students}
            
            # Return students in the order they were checked in, with names
            student_names = [
                {
                    "studentID": sid,
                    "name": student_map.get(sid, f"Student {sid}")
                }
                for sid in student_ids
            ]
        except Exception as e:
            print(f"Error fetching student names: {e}")
            # Fallback: just return IDs if we can't get names
            student_names = [{"studentID": sid, "name": f"Student {sid}"} for sid in student_ids]
    
    return {
        "eventID": event_id,
        "checkedIn": student_ids,
        "checkedInStudents": student_names,
        "count": len(student_ids)
    }


@app.post("/events/{event_id}/finalize")
def finalize_event(event_id: int):
    """
    Finalizes attendance:
    - Saves all registered attendees to MySQL
    - Saves unregistered (walk-in) attendees to MongoDB
    - Clears Redis keys
    Returns event attendance summary
    """
    try:
        # Validate event exists
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT eventID FROM Event WHERE eventID = %s;", (event_id,))
        event = cursor.fetchone()
        if not event:
            cursor.close()
            db.close()
            raise HTTPException(status_code=404, detail=f"Event {event_id} not found")
        
        attendees_key = f"event:{event_id}:attendees"
        attendees_raw = list(redis_client.smembers(attendees_key))
        
        # Convert Redis values (bytes or strings) to integers and deduplicate
        attendees_set = set()
        for s in attendees_raw:
            try:
                student_id = int(s.decode()) if isinstance(s, bytes) else int(s)
                attendees_set.add(student_id)
            except (ValueError, AttributeError):
                # Skip invalid student IDs
                continue
        
        # Convert to list for processing
        attendees = list(attendees_set)

<<<<<<< HEAD
    db = mysql_connect()
    cursor = db.cursor()
    registered = []
    walk_ins = []
    for student_id in attendees:
        cursor.execute(
            "SELECT 1 FROM Registration WHERE studentID=%s AND eventID=%s",
            (student_id, event_id)
        )  # Check if student is registered
        is_registered = cursor.fetchone()

        if is_registered:
=======
        # Delete existing finalized data for this event before saving new data
        # This allows re-finalizing to override previous finalized data
        cursor.execute("DELETE FROM Attendance WHERE eventID = %s;", (event_id,))
        mongo_db["walk_ins"].delete_many({"eventID": event_id})
        
        registered = []
        walk_ins = []
        
        # Get current timestamp for walk-ins
        current_time = datetime.now()
        
        for student_id in attendees:
>>>>>>> ff2f150 (Students and SmallGroups in Leader Dashboard on frontend working)
            cursor.execute(
                "SELECT 1 FROM Registration WHERE studentID=%s AND eventID=%s",
                (student_id, event_id)
<<<<<<< HEAD
            )  # Save registered to MySQL
            registered.append(student_id)
        else:
            mongo_db["walk_ins"].insert_one({
                "eventID": event_id,
                "studentID": student_id
            })  # Save walk-ins to MongoDB
            walk_ins.append(student_id)
    db.commit()
    cursor.close()
    db.close()
=======
            ) #Check if student is registered
            is_registered = cursor.fetchone()
>>>>>>> ff2f150 (Students and SmallGroups in Leader Dashboard on frontend working)

            if is_registered:
                cursor.execute(
                    "INSERT INTO Attendance (studentID, eventID, checkInTime) VALUES (%s, %s, NOW())",
                    (student_id, event_id)
                ) #Save registered to MySQL
                registered.append(student_id)
            else:
                mongo_db["walk_ins"].insert_one({
                    "eventID": event_id,
                    "studentID": student_id,
                    "checkInTime": current_time
                }) #Save walk-ins to MongoDB with check-in time
                walk_ins.append(student_id)
        
        db.commit()
        cursor.close()
        db.close()

<<<<<<< HEAD
    return {
        "message": "Event finalized successfully",
        "eventID": event_id,
        "registeredSaved": registered,
        "walkInsLogged": walk_ins,
        "totalRegistered": len(registered),
        "totalWalkIns": len(walk_ins),
        "totalAttendees": len(registered) + len(walk_ins)
    }
# GraphQL setup:
from strawberry.fastapi import GraphQLRouter
from graphql_schema import schema

# GraphQL router:
graphql_app = GraphQLRouter(schema, graphiql=True)

# Adding the router to the FastAPI application
app.include_router(graphql_app, prefix="/graphql")

@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Serves the demo HTML page.
    """
    return os.path.join(os.path.dirname(__file__), "index.html")
=======
        redis_client.delete(f"event:{event_id}:checkedIn")
        redis_client.delete(attendees_key)

        return {
            "message": "Event finalized successfully",
            "eventID": event_id,
            "registeredSaved": registered,
            "walkInsLogged": walk_ins,
            "totalRegistered": len(registered),
            "totalWalkIns": len(walk_ins),
            "totalAttendees": len(registered) + len(walk_ins)
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"Finalize error: {e}")
        raise HTTPException(status_code=500, detail=f"Finalization failed: {str(e)}")

@app.get("/events/{event_id}/attendance")
def get_event_attendance(event_id: int):
    """
    Retrieves finalized attendance data for an event:
    - Registered attendees from MySQL Attendance table
    - Walk-ins from MongoDB walk_ins collection
    Returns combined attendance with student names
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        
        # Get registered attendees from MySQL - deduplicate by studentID
        cursor.execute("""
            SELECT 
                a.studentID,
                s.firstName,
                s.lastName
            FROM Attendance a
            JOIN Student s ON a.studentID = s.studentID
            WHERE a.eventID = %s
            GROUP BY a.studentID, s.firstName, s.lastName
            ORDER BY a.studentID;
        """, (event_id,))
        registered_attendees = cursor.fetchall()
        
        # Get walk-ins from MongoDB - deduplicate
        walk_ins_raw = list(mongo_db["walk_ins"].find({"eventID": event_id}, {"_id": 0}))
        
        # Deduplicate walk-ins by studentID, keeping the earliest check-in time
        walk_ins_deduped = {}
        for walk_in in walk_ins_raw:
            student_id = walk_in["studentID"]
            check_in_time = walk_in.get("checkInTime")
            
            if student_id not in walk_ins_deduped:
                walk_ins_deduped[student_id] = walk_in
            else:
                # Keep the earliest check-in time
                existing_time = walk_ins_deduped[student_id].get("checkInTime")
                if check_in_time and (not existing_time or check_in_time < existing_time):
                    walk_ins_deduped[student_id] = walk_in
        
        walk_in_ids = list(walk_ins_deduped.keys())
        
        # Get student names for walk-ins
        walk_ins_with_names = []
        if walk_in_ids:
            placeholders = ','.join(['%s'] * len(walk_in_ids))
            cursor.execute(
                f"SELECT studentID, firstName, lastName FROM Student WHERE studentID IN ({placeholders})",
                walk_in_ids
            )
            walk_in_students = cursor.fetchall()
            student_map = {s["studentID"]: s for s in walk_in_students}
            
            for student_id, walk_in in walk_ins_deduped.items():
                student = student_map.get(student_id, {})
                check_in_time = walk_in.get("checkInTime")
                # Format check-in time if it exists
                if check_in_time:
                    if isinstance(check_in_time, datetime):
                        check_in_time_str = check_in_time.strftime("%Y-%m-%d %H:%M:%S")
                    else:
                        check_in_time_str = str(check_in_time)
                else:
                    check_in_time_str = None
                
                walk_ins_with_names.append({
                    "studentID": student_id,
                    "firstName": student.get("firstName", "Unknown"),
                    "lastName": student.get("lastName", ""),
                    "checkInTime": check_in_time_str,
                    "isWalkIn": True
                })
        
        cursor.close()
        db.close()
        
        # Format registered attendees (no check-in time for registered)
        registered_formatted = [
            {
                "studentID": r["studentID"],
                "firstName": r["firstName"],
                "lastName": r["lastName"],
                "isWalkIn": False
            }
            for r in registered_attendees
        ]
        
        # Check if event has been finalized (has any attendance data)
        has_finalized_data = len(registered_formatted) > 0 or len(walk_ins_with_names) > 0
        
        return {
            "eventID": event_id,
            "registered": registered_formatted,
            "walkIns": walk_ins_with_names,
            "totalRegistered": len(registered_formatted),
            "totalWalkIns": len(walk_ins_with_names),
            "totalAttendees": len(registered_formatted) + len(walk_ins_with_names),
            "hasFinalizedData": has_finalized_data
        }
    except Exception as e:
        print(f"Get attendance error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve attendance: {str(e)}")
>>>>>>> ff2f150 (Students and SmallGroups in Leader Dashboard on frontend working)
