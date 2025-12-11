import strawberry
import datetime
from typing import Optional, List
from strawberry.scalars import JSON
from fastapi import HTTPException

from main import (
    list_tables,
    get_all_students,
    get_student_by_id,
    get_groups,
    get_all_events,
    create_event,
    get_event_data,
    check_in,
    check_out,
    live_attendance,
    finalize_event,
    get_finalized_attendance_view,
)

def dict_to_student(s: dict) -> "Student":
    """Helper to convert dict to Student"""
    return Student(
        studentID=s["studentID"],
        firstName=s["firstName"],
        lastName=s["lastName"],
        age=s["age"],
        phoneNumber=s.get("phoneNumber"),
        email=s.get("email"),
        groupID=s["groupID"],
        guardians=s.get("guardians", [])
    )

def dict_to_event(e: dict) -> "Event":
    """Helper to convert dict to Event"""
    return Event(
        eventID=e["eventID"],
        name=e.get("name"),
        location=e["location"],
        date=e["date"],
        time=e["time"],
        customFields=e.get("customFields")
    )

@strawberry.type
class Guardian:
    guardianID: int
    firstName: str
    lastName: str
    phoneNumber: Optional[str]
    email: Optional[str]


@strawberry.type
class SmallGroup:
    groupID: int
    name: Optional[str]
    members: List["Student"]


@strawberry.type
class Event:
    eventID: int
    name: Optional[str]
    location: str
    date: datetime.date
    time: str
    customFields: Optional[JSON] = None


@strawberry.type
class Student:
    studentID: int
    firstName: str
    lastName: str
    age: int
    phoneNumber: Optional[str]
    email: Optional[str]
    groupID: int
    guardians: List[str]


# Response Types


@strawberry.type
class RootMessage:
    message: str
    tables: List[str]


@strawberry.type
class EventResponse:
    message: str
    eventID: int
    customFields: Optional[JSON]


@strawberry.type
class CheckInResponse:
    message: str
    eventID: int
    studentID: int


@strawberry.type
class CheckOutResponse:
    message: str
    eventID: int
    studentID: int


@strawberry.type
class LiveAttendanceStudent:
    studentID: int
    name: str


@strawberry.type
class LiveAttendanceResponse:
    eventID: int
    checkedIn: List[int]
    count: int
    checkedInStudents: List[LiveAttendanceStudent]


@strawberry.type
class FinalizeEventResponse:
    message: str
    eventID: int
    registeredSaved: List[int]
    walkInsLogged: List[int]
    totalRegistered: int
    totalWalkIns: int
    totalAttendees: int


@strawberry.type
class FinalizedAttendanceStudent:
    studentID: int
    firstName: str
    lastName: str
    isWalkIn: bool


@strawberry.type
class FinalizedAttendanceView:
    eventID: int
    status: str
    message: str
    registered: List[FinalizedAttendanceStudent]
    walkIns: List[FinalizedAttendanceStudent]
    totalRegistered: int
    totalWalkIns: int
    totalAttendees: int
    hasFinalizedData: bool


# Query Resolvers


@strawberry.type
class Query:

    @strawberry.field
    def root(self) -> RootMessage:
        return RootMessage(
            message="Welcome to the Youth Group API!",
            tables=list_tables()
        )

    @strawberry.field
    def students(self) -> List[Student]:
        return [dict_to_student(s) for s in get_all_students()]

    @strawberry.field
    def student(self, student_id: int) -> Optional[Student]:
        try:
            get_student_by_id(student_id)
        except HTTPException:
            return None
        all_students = get_all_students()
        formatted = next((s for s in all_students if s["studentID"] == student_id), None)
        return dict_to_student(formatted) if formatted else None

    @strawberry.field
    def groups(self) -> List[SmallGroup]:
        groups_data = get_groups()
        students_dict = {s["studentID"]: s for s in get_all_students()}
        return [
            SmallGroup(
                groupID=g["groupID"],
                name=g.get("name"),
                members=[dict_to_student(students_dict.get(m["studentID"], m)) for m in g.get("members", [])]
            )
            for g in groups_data
        ]

    @strawberry.field
    def events(self) -> List[Event]:
        return [dict_to_event(e) for e in get_all_events()]

    @strawberry.field
    def event(self, event_id: int) -> Optional[Event]:
        try:
            return dict_to_event(get_event_data(event_id))
        except HTTPException:
            return None

    @strawberry.field
    def liveAttendance(self, event_id: int) -> LiveAttendanceResponse:
        data = live_attendance(event_id)
        # Convert to LiveAttendanceResponse object
        checked_in_students = [
            LiveAttendanceStudent(
                studentID=s["studentID"],
                name=s["name"]
            )
            for s in data.get("checkedInStudents", [])
        ]
        return LiveAttendanceResponse(
            eventID=data["eventID"],
            checkedIn=data.get("checkedIn", []),
            count=data.get("count", 0),
            checkedInStudents=checked_in_students
        )

    @strawberry.field
    def finalizedAttendance(self, event_id: int) -> FinalizedAttendanceView:
        """Get finalized attendance data for an event"""
        data = get_finalized_attendance_view(event_id)
        # Convert dictionaries to FinalizedAttendanceView object
        registered = [
            FinalizedAttendanceStudent(
                studentID=r["studentID"],
                firstName=r["firstName"],
                lastName=r["lastName"],
                isWalkIn=False
            )
            for r in data.get("registered", [])
        ]
        walk_ins = [
            FinalizedAttendanceStudent(
                studentID=w["studentID"],
                firstName=w["firstName"],
                lastName=w["lastName"],
                isWalkIn=True
            )
            for w in data.get("walkIns", [])
        ]
        return FinalizedAttendanceView(
            eventID=data["eventID"],
            status=data.get("status", "unknown"),
            message=data.get("message", ""),
            registered=registered,
            walkIns=walk_ins,
            totalRegistered=data.get("totalRegistered", 0),
            totalWalkIns=data.get("totalWalkIns", 0),
            totalAttendees=data.get("totalAttendees", 0),
            hasFinalizedData=data.get("hasFinalizedData", False)
        )


# Mutation Resolvers


@strawberry.type
class Mutation:

    @strawberry.mutation
    def createEvent(self, name: str, location: str, date: str, time: str, customFields: Optional[JSON] = None) -> Event:
        return dict_to_event(create_event({"name": name, "location": location, "date": date, "time": time, "customFields": customFields or {}}))

    @strawberry.mutation
    def checkIn(self, event_id: int, student_id: int) -> CheckInResponse:
        data = check_in(event_id, student_id)
        return CheckInResponse(
            message=data["message"],
            eventID=data["eventID"],
            studentID=data["studentID"]
        )

    @strawberry.mutation
    def checkOut(self, event_id: int, student_id: int) -> CheckOutResponse:
        data = check_out(event_id, student_id)
        return CheckOutResponse(
            message=data["message"],
            eventID=data["eventID"],
            studentID=data["studentID"]
        )

    @strawberry.mutation
    def finalizeEvent(self, event_id: int) -> FinalizeEventResponse:
        data = finalize_event(event_id)
        return FinalizeEventResponse(
            message=data["message"],
            eventID=data["eventID"],
            registeredSaved=data.get("registeredSaved", []),
            walkInsLogged=data.get("walkInsLogged", []),
            totalRegistered=data.get("totalRegistered", 0),
            totalWalkIns=data.get("totalWalkIns", 0),
            totalAttendees=data.get("totalAttendees", 0)
        )


# Build Schema

schema = strawberry.Schema(query=Query, mutation=Mutation)