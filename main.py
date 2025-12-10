import os
import mysql.connector
import redis
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
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)

        cursor.execute("SELECT * FROM SmallGroup")
        groups = cursor.fetchall()

        cursor.execute("SELECT * FROM Student")
        students = cursor.fetchall()

        cursor.close()
        db.close()

        for g in groups:
            g["members"] = [s for s in students if s["groupID"] == g["groupID"]]

        return groups

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/events")
def get_all_events():
    """
    Retrieves a list of all events from MySQL.
    """
    try:
        db = mysql_connect()
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            "SELECT eventID, name, location, date, CAST(time AS CHAR) AS time FROM Event ORDER BY date, time;")
        events = cursor.fetchall()
        cursor.close()
        db.close()
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
    """
    redis_client.sadd(f"event:{event_id}:checkedIn", student_id)
    redis_client.sadd(f"event:{event_id}:attendees", student_id)
    return {"message": "checked in", "eventID": event_id, "studentID": student_id}


@app.post("/events/{event_id}/checkout/{student_id}")
def check_out(event_id: int, student_id: int):
    """
    Check a student out with Redis
    """
    redis_client.srem(f"event:{event_id}:checkedIn", student_id)
    return {"message": "checked out", "eventID": event_id, "studentID": student_id}


@app.get("/events/{event_id}/live")
def live_attendance(event_id: int):
    """
    Returns the live attendance of an event with Redis
    """
    key = f"event:{event_id}:checkedIn"
    students = list(redis_client.smembers(key))
    return {"eventID": event_id, "checkedIn": students, "count": len(students)}


@app.post("/events/{event_id}/finalize")
def finalize_event(event_id: int):
    """
    Finalizes attendance:
    - Saves all registered attendees to MySQL
    - Saves unregistered (walk-in) attendees to MongoDB
    - Clears Redis keys
    Returns event attendance summary
    """
    attendees_key = f"event:{event_id}:attendees"
    attendees = list(redis_client.smembers(attendees_key))

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
            cursor.execute(
                "INSERT IGNORE INTO Attendance (studentID, eventID, checkInTime) VALUES (%s, %s, NOW())",
                (student_id, event_id)
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
