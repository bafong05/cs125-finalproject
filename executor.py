
import http.server
import json
import mysql.connector

DB_USER = "root"
DB_PASSWORD = "<YOUR PASSWORD HERE>"
DB_HOST = "127.0.0.1"
DB_NAME = "youth_group"

def get_students():
    cnx = mysql.connector.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        database=DB_NAME
    )
    cursor = cnx.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Student LIMIT 5;")
    rows = cursor.fetchall()
    cursor.close()
    cnx.close()
    return rows

class Handler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/students":
            data = get_students()
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode())
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server = http.server.HTTPServer(("127.0.0.1", 5000), Handler)
    print("Server running at http://127.0.0.1:5000")
    server.serve_forever()

# import mysql.connector
# from mysql.connector import errorcode

# # NOTE: Update with your database credentials
# DB_USER = "root"
# DB_PASSWORD = "<YOUR PASSWORD HERE>"
# DB_HOST = "127.0.0.1"
# DB_NAME = "youth_group"


# def main():
#     """
#     Demonstrates basic database operations.
#     """
#     try:
#         # Establish a connection to the database
#         cnx = mysql.connector.connect(
#             user=DB_USER,
#             password=DB_PASSWORD,
#             host=DB_HOST,
#             database=DB_NAME
#         )
#         print("Successfully connected to the database.")

#         # Create a cursor
#         cursor = cnx.cursor()

#         # Execute a query
#         query = """
#             SELECT studentID, firstName, lastName 
#             FROM Student
#             ORDER BY lastName, firstName
#             LIMIT 5;
#         """
#         cursor.execute(query)

#         # Fetch and print the results
#         print("\nFirst 5 students:")
#         for (studentID, firstName, lastName) in cursor.fetchall():
#             print(f"  - [ID: {studentID}] {firstName} {lastName}")
    
#         # Close the cursor and connection
#         cursor.close()
#         cnx.close()
#         print("\nConnection closed.")

#     except mysql.connector.Error as err:
#         if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
#             print("Something is wrong with your user name or password")
#         elif err.errno == errorcode.ER_BAD_DB_ERROR:
#             print("Database does not exist")
#         else:
#             print(err)


# if __name__ == '__main__':
#     main()
