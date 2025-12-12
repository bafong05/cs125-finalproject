# Youth Group Database Management System

**Westmont College Fall 2025**

**CS 125 Database Design**

*Professor* Mike Ryu (mryu@westmont.edu)

## Author Information

* **Team Name**: Backcourt (Bailey Fong, James Dodson)
* **Email(s)**: bafong@westmont.edu, jdodson@westmont.edu

## Running the Backend (Docker)

### 1. Clone the Repository

```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Set Up Secrets

Create a `secrets/` directory at the project root with the following files:

```
secrets/
├── mysql_password.txt
├── mongo_url.txt
└── redis_password.txt
```

Each file should contain only the secret value (no extra whitespace or newlines).

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize Databases

If running the project for the first time, initialize the databases:

```bash
mysql -u root -p < schema.sql
mysql -u root -p < data.sql
python3 setup_mongo.py
```

### 5. Run the Docker Container

1. **Build the Docker Image:**

   ```bash
   docker build -t youth-group-api .
   ```

2. **Run the Docker Container:**

   ```bash
   docker run --name youth-group-api \
     --network cs125-net \
     -p 8000:8000 \
     youth-group-api
   ```

## Access Points

Once the application is running:

* **Dashboard:** http://127.0.0.1:8000
* **GraphQL API (GraphiQL):** http://127.0.0.1:8000/graphql
* **REST API Docs:** http://127.0.0.1:8000/docs

## GraphQL Examples

The following examples can be run in the GraphiQL interface at `http://127.0.0.1:8000/graphql`.

### Queries

#### Get All Students

```graphql
query GetAllStudents {
  students {
    studentID
    firstName
    lastName
    age
    email
    phoneNumber
    groupID
  }
}
```

#### Get a Single Student by ID

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

#### Get Live Attendance

Retrieves live attendance data combining Redis (current check-ins), MySQL (registered students), and MongoDB (walk-ins).

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

### Mutations

#### Create an Event

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
