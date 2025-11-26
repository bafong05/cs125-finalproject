import http.server
import json
import mysql.connector

DB_USER = "root"
DB_PASSWORD = "cs125"
DB_HOST = "127.0.0.1"
DB_PORT = 3306
DB_NAME = "youth_group"

def get_table(table_name):
    cnx = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM {table_name} LIMIT 5;")
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path.startswith("/") and len(self.path) > 1:
            table = self.path[1:]
            try:
                data = get_table(table)
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps(data).encode())
            except Exception:
                self.send_response(500)
                self.end_headers()
            return
        self.send_response(404)
        self.end_headers()

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", 5000), Handler)
    server.serve_forever()
