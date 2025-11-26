import http.server
import json
import mysql.connector

DB_USER = "root"
DB_PASSWORD = "cs125"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "youth_group"

def list_tables():
    cnx = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    cursor = cnx.cursor()
    cursor.execute("SHOW TABLES;")
    tables = [row[0] for row in cursor.fetchall()]
    cursor.close()
    cnx.close()
    return tables

def get_table(real_name):
    cnx = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)
    cursor.execute(f"SELECT * FROM `{real_name}` LIMIT 50;")
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path

        if path == "/":
            tables = list_tables()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(tables).encode())
            return

        if path.startswith("/") and len(path) > 1:
            requested = path[1:].rstrip("/")

            all_tables = list_tables()
            lookup = {t.lower(): t for t in all_tables}
            key = requested.lower()

            if key in lookup:
                real_name = lookup[key]
                try:
                    data = get_table(real_name)
                    self.send_response(200)
                    self.send_header("Content-Type", "application/json")
                    self.end_headers()
                    self.wfile.write(json.dumps(data).encode())
                except:
                    self.send_response(500)
                    self.end_headers()
                return

            self.send_response(404)
            self.end_headers()
            return

        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    print("Starting server on http://127.0.0.1:5000")
    server = http.server.HTTPServer(("127.0.0.1", 5000), Handler)
    server.serve_forever()
