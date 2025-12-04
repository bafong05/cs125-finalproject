import os
import json
import mysql.connector
from dotenv import load_dotenv
from pymongo import MongoClient
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse

load_dotenv()

DB_USER = os.getenv("MYSQL_USER")
DB_PASS = os.getenv("MYSQL_PASSWORD")
DB_HOST = "mysql-cs125"
DB_PORT = 3306
DB_NAME = "youth_group"

if not DB_USER or not DB_PASS:
    raise Exception("Missing MySQL environment variables")

MONGO_URL = os.getenv("MONGO_URL")
if not MONGO_URL:
    raise Exception("Missing Mongo URL.")

mongo_client = MongoClient(MONGO_URL)
mongo_db = mongo_client["youth_group"]

app = FastAPI()

def mysql_connect():
    return mysql.connector.connect(
    user=DB_USER,
    password=DB_PASS,
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME
    )

def get_students_in_group(group_id):
    db = mysql_connect()
    cursor = db.cursor(dictionary=True)
    cursor.execute(
        "SELECT * FROM Student WHERE groupId = %s",
        (group_id,)
    )
    rows = cursor.fetchall()
    cursor.close()
    db.close()
    return rows


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

@app.get("/")
def all_tables():
    """Return list of all MySQL tables."""
    return list_tables()


@app.get("/{table_name}")
def get_table(table_name: str):
    """Return table data, case-insensitive."""
    all_tables = list_tables()
    lookup = {t.lower(): t for t in all_tables}

    if table_name.lower() not in lookup:
        raise HTTPException(status_code=404, detail="Table not found")

    return get_table(lookup[table_name.lower()])


@app.get("/groups/{group_id}/students")
def students_in_group(group_id: int):
    students = get_students_in_group(group_id)

    if not students:
        raise HTTPException(status_code=404, detail="No students found for this group")

    return students