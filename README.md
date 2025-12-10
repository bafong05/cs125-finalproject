# Youth Group Database Management System
**Westmont College Fall 2025**

**CS 125 Database Design**

*Professor* Mike Ryu (mryu@westmont.edu) 

## Author Information
* **Team Name**: Backcourt (Bailey Fong, James Dodson)
* **Email(s)**: bafong@westmont.edu, jdodson@westmont.edu

## Execution/Demo Instructions

To run the complete demo, follow these steps in order:

1. **Install Dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

2. **Set up the Databases:**

    You need to run the setup scripts to populate the databases with sample data.

    *   **MySQL:** Make sure your MySQL server is running and that you have created the `youth_group` database and its tables by executing the `schema.sql` script, then populate it with sample data using `data.sql`.

    *   **MongoDB:** Run the MongoDB setup script:

        ```bash
        python3 setup_mongo.py
        ```

    *   **Redis:** Redis will be used automatically for live attendance tracking. Make sure your Redis server is running.

3. **Set up Secrets:**

    Create a `secrets` directory in the project root and add files containing your credentials:
    - `mysql_password.txt`: Your MySQL root password
    - `mongo_url.txt`: Your MongoDB connection string
    - `redis_password.txt`: Your Redis password (if required)

4. **Run the FastAPI Server:**

    Start the application from the project root:

    ```bash
    uvicorn main:app --reload --port 8000
    ```

5.  **Access the Demo:**

    *   Open your web browser and go to **http://127.0.0.1:8000** to see the Youth Group Dashboard. The dashboard includes:
        - **Leader Dashboard**: Manage students, small groups, events, and attendance
        - **Student Dashboard**: View student information, upcoming events, and attendance history
        - **GraphQL Explorer**: Interactive tool to test GraphQL queries and mutations

    *   Go to **http://127.0.0.1:8000/graphql** to interact with the GraphQL API via the GraphiQL interface.

    *   Go to **http://127.0.0.1:8000/docs** to see the REST API documentation.

## Running the Backend in Docker

1.  **Build the Docker Image:**

    From the project root directory, run the `docker build` command:

    ```bash
    docker build -t youth-group-api .
    ```

2.  **Run the Docker Container:**

    The command to run the container differs slightly depending on your operating system due to how Docker networking is handled.

    **For Docker Desktop (macOS or Windows):**

    Docker Desktop provides a special DNS name `host.docker.internal` that containers can use to connect to services running on the host machine. The `Dockerfile` is already configured to use this.

    Execute this command from your project root:

    ```bash
    docker run --rm -it \
      -p 8000:8000 \
      -v "$(pwd)/secrets:/app/secrets" \
      youth-group-api
    ```
3.  **Access the Demo:**

    Once the container is running, the API and demo page are available at the same URLs as before:

    *   **Dashboard:** http://127.0.0.1:8000
    *   **GraphQL API:** http://127.0.0.1:8000/graphql
    *   **REST API Docs:** http://127.0.0.1:8000/docs

## Sample GraphQL Queries

Here are some example queries you can run in the GraphiQL interface (available at `http://127.0.0.1:8000/graphql`) to see how the API works.

---

### Query 1: Get All Students (Basic)

This query fetches a list of all students, only asking for their first and last names

```graphql
query GetAllStudents {
  students {
    firstName
    lastName
  }
}
```

---

### Query 2: Get a Single Student by ID

This query uses an argument (`student_id`) to fetch a specific student.

```graphql
query GetStudentById {
  student(studentId: 1) {
    studentID
    firstName
    lastName
    age
    email
    phoneNumber
    guardians
    groupID
  }
}
```

---

### Query 3: The "Trifecta" - Live Attendance

This query retrieves live attendance data that combines Redis (current check-ins), MySQL (registered students), and MongoDB (walk-ins).

```graphql
query GetLiveAttendance {
  liveAttendance(eventId: 1) {
    eventID
    count
    checkedIn
    checkedInStudents {
      studentID
      name
    }
  }
}
```

---

### Query 4: Get Finalized Attendance

This query retrieves finalized attendance data that combines MySQL (registered attendees) and MongoDB (walk-ins) after an event has been finalized.

```graphql
query GetFinalizedAttendance {
  finalizedAttendance(eventId: 1) {
    eventID
    totalAttendees
    totalRegistered
    totalWalkIns
  }
}
```

---

### Mutation 1: Create an Event

This mutation creates a new event with custom fields stored in MongoDB.

```graphql
mutation CreateEvent {
  createEvent(
    name: "Summer Camp"
    location: "Beachside Park"
    date: "2026-07-15"
    time: "09:00:00"
    customFields: {
      packingList: ["sleeping bag", "water bottle", "Bible"]
      bringFriend: true
    }
  ) {
    eventID
    name
    location
    date
    time
    customFields
  }
}
```

---

### Mutation 2: Check In a Student

This mutation checks in a student for an event.

```graphql
mutation CheckInStudent {
  checkIn(eventId: 1, studentId: 1) {
    message
    eventID
    studentID
  }
}
```

---

### Mutation 3: Finalize an Event

This mutation finalizes an event, moving attendance data from Redis to permanent storage in MySQL (registered attendees) and MongoDB (walk-ins).

```graphql
mutation FinalizeEvent {
  finalizeEvent(eventId: 1) {
    message
    eventID
    totalRegistered
    totalWalkIns
    totalAttendees
    registeredSaved
    walkInsLogged
  }
}
```