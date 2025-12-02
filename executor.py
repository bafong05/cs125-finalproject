import http.server
import json
import mysql.connector
from dotenv import load_dotenv
import os
from pymongo import MongoClient


load_dotenv()

DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "youth_group"

if not DB_USER or not DB_PASS:
    raise Exception("Missing MySQL environment variables")

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise Exception("Missing Mongo URL.")

mongo_client = MongoClient(MONGO_URL,tls=True,tlsAllowInvalidCertificates=True)
mongo_db = mongo_client["youth_group"]

def mysql_connect():
    return mysql.connector.connect(
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
    )

def insert_event_type(typeName):
    db = mysql_connect()
    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO EventType (typeName) VALUES (%s)", (typeName,))
        db.commit()
        return cursor.lastrowid
    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:
            cursor.execute("SELECT typeId FROM EventType WHERE typeName = %s", (typeName,))
            return cursor.fetchone()[0]
        raise
    finally:
        cursor.close()
        db.close()

def save_event_type(typeId, typeName, fields):
    mongo_db["eventTypes"].insert_one({
            "typeId": typeId,
            "typeName": typeName,
            "fields": fields
        })

def list_tables():
    db = mysql_connect()
    cursor = db.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    db.close()
    return tables

def get_table(name):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM `{name}` LIMIT 50;")
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.strip("/")

        if path == "":
            tables = list_tables()
            self.send_json(tables)
            return

        all_tables = list_tables()
        lookup = {t.lower(): t for t in all_tables}

        if path.lower() in lookup:
            data = get_table(lookup[path.lower()])
            self.send_json(data)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/event-types":
            self.send_error(404)
            return

        length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(length)

        try:
            data = json.loads(body)
        except:
            self.send_error(400, "Invalid JSON")
            return

        typeName = data.get("typeName")
        fields = data.get("fields", [])

        if not typeName:
            self.send_response(400, "Missing typeName")
            return

        typeId = insert_event_type(typeName)
        save_event_type(typeId, typeName, fields)

        self.send_json({"typeID": typeId}, status = 201)

        print("Inserted EventType:", typeId)

        save_event_type(typeId, typeName, fields)
        print("Saved schema in MongoDB")

    def send_json(self, obj, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(obj).encode())

if __name__ == "__main__":
    print("Starting server on http://127.0.0.1:5000")
    server = http.server.HTTPServer(("127.0.0.1", 5000), Handler)
    server.serve_forever()
