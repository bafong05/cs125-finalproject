# Youth Group Database Management System
**Westmont College Fall 2025**

**CS 125 Database Design**

*Professor* Mike Ryu (mryu@westmont.edu) 

## Author Information
* **Team Name**: Backcourt (Bailey Fong, James Dodson)
* **Email(s)**: bafong@westmont.edu, jdodson@westmont.edu

1. **Open your terminal in the project root directory and run:**

    ```bash
    pip install -r requirements.txt
    ```

2.  **Set up the Databases:**

    You need to run the setup scripts to populate the databases with sample data.

    *   **MySQL:** Make sure your MySQL server is running and that you have created the `youth_group` database and its tables by executing the `schema.sql` script, then populate it with sample data using `data.sql`.

    *   **MongoDB:** Run the MongoDB setup script:

        ```bash
        python3 setup_mongo.py
        ```

    *   **Redis:** Redis will be used automatically for live attendance tracking. Make sure your Redis server is running.

3.  **Set up Secrets:**

    Create a `secrets` directory in the project root and add a file named `mysql_password.txt` containing your MySQL root password.

4.  **Run the FastAPI Server:**

    Start the application from the project root:

    ```bash
    uvicorn main:app --reload --port 8000
    ```

5.  **Access the Demo:**

    *   Open your web browser and go to **http://127.0.0.1:8000** to see the Youth Group Dashboard (frontend is in `youth_group_frontend/index.html`).

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

This query fetches a list of all students, but only asks for their first and last names. This demonstrates GraphQL's ability to select only the data you need.

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

This query uses an argument (`student_id`) to fetch a specific student. You can change the `student_id` value in GraphiQL to get different results.

```graphql
query GetStudentById {
  student(studentId: 1) {
    studentID
    firstName
    lastName
    age
    email
    guardians
  }
}
```

---

### Query 3: The "Trifecta" - Live Attendance

This query showcases the power of GraphQL to fetch complex, nested data from multiple sources (Redis, MySQL, MongoDB) in a single request. It retrieves live attendance data that combines Redis (current check-ins), MySQL (registered students), and MongoDB (walk-ins).

```graphql
query GetLiveAttendance {
  liveAttendance(eventId: 1) {
    eventID
    checkedInCount
    checkedInStudents {
      studentID
      firstName
      lastName
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
    eventName
    totalAttendees
    totalRegistered
    totalWalkIns
    registered {
      studentID
      firstName
      lastName
    }
    walkIns {
      studentID
      firstName
      lastName
    }
  }
}
```

---

### Query 5: Using Aliases

Aliases let you rename the result of a field to anything you want. This is useful for fetching the same type of object with different arguments in a single query.

```graphql
query GetMultipleStudents {
  firstStudent: student(studentId: 1) {
    studentID
    firstName
    lastName
  }
  secondStudent: student(studentId: 2) {
    studentID
    firstName
    lastName
  }
}
```

---

### Query 6: Get Events with Custom Fields

This query fetches all events, including their custom fields stored in MongoDB. This demonstrates how GraphQL can seamlessly combine data from MySQL (core event info) and MongoDB (custom fields).

```graphql
query GetEventsWithCustomFields {
  events {
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

### Query 7: Using Fragments

Fragments are reusable sets of fields. They help you avoid repeating the same fields in multiple places. Here, we define a fragment `studentFields` and use it in multiple queries.

```graphql
query GetStudentsAndGroups {
  students {
    ...studentFields
  }
  groups {
    groupID
    name
    members {
      ...studentFields
    }
  }
}

fragment studentFields on Student {
  studentID
  firstName
  lastName
  age
  email
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
    message
    event {
      eventID
      name
      location
      customFields
    }
  }
}
```

---

### Mutation 2: Check In a Student

This mutation checks in a student for an event, updating Redis in real-time.

```graphql
mutation CheckInStudent {
  checkIn(eventId: 1, studentId: 1) {
    message
    eventID
    studentID
    checkedIn
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
  }
}
```
