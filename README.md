# Final Project
**Westmont College Fall 2025**

**CS 125 Database Design**

*Assistant Professor* Mike Ryu (mryu@westmont.edu) 

## Author Information
* **Name(s)**: Bailey Fong, James Dodson
* **Email(s)**: bafong@westmont.edu, jdodson@westmont.edu


**Team name:**
- Backcourt

**Who is using this?**
- James’ church youth group, which has small groups, check-in, attendance, among other things.

**What do they want to do?**
- Keep track of attendance, live check-in (which may also be useful for events), small groups, and record small group summaries

**What should they be able to do?**
- Update/change student information, event information, small group info (members, leader(s))

**What shouldn’t they be able to do?**
- Change date-specific small-group info (for example, notes that were taken and attendance that day)
- Change attendance after the day it’s recorded
- Delete past information (events, attendance)

**11/25/25:**  
Using Python, we create a connection to our database in Insomnia, and then create a cursor, and by entering in the SQL commands as a string, we can execute any SQL query we want, but we then have to gather and print the results afterwards. However, this means that we can sort all of our data by any metric we want, and get as specific as we need to. Lastly, both the cursor and connection need to be closed so that resources aren't wasted keeping them open for no reason.

To spin up the server:
- Start the existing MySQL container
- Load the database schema and data
- Start the API: python3 executor.py
- Use Insomnia to test the server: GET request http://127.0.0.1:5000/students

In browser:
- http://127.0.0.1:5000/ returns all table names
- http://127.0.0.1:5000/<table_name> returns rows from specific table

**12/5/25:**  
Technologies used:
- FastAPI —> main backend framework
- MySQL —> primary relational database
- MongoDB —> stores custom event data + walk-ins
- Redis —> real-time check-in / check-out tracking
  
*Event data:*
- Core event info is stored in MySQL (Event(eventID, name, location, date, time))
- Custom event fields are stored in MongoDB
  - Example MongoDB document:  
    {"eventID": 1001,  
    "customFields": {  
        "packingList": ["sleeping bag", "water bottle"],  
        "bringFriend": true}}  
    
*Endpoints:*  
- POST /events
  - Creates the MySQL event
  - Stores optional customFields in MongoDB
- GET /events/{event_id}
  - Returns merged MySQL + MongoDB data

*Event attendance:*  
- Redis tracks live attendance with check ins and check outs
  
*Endpoints:*  
- POST /events/{event_id}/checkin/{student_id}
  - Adds a student to checkedIn and attendees sets
- POST /events/{event_id}/checkout/{student_id}
  - Removes student from checkedIn but keeps them in attendees set
- GET /events/{event_id}/live
  - Returns students currently present
- POST /events/{event_id}/finalize
  - At the end of an event, all attendance is permanently saved
    - Registered attendees are saved to MySQL Attendance
    - Walk-ins are stored in a MongoDB walk_ins
    - Redis keys are deleted
   
To run:
1. pip install -r requirements.txt
2. uvicorn main:app --reload --port 8000
3. http://127.0.0.1:8000/docs
