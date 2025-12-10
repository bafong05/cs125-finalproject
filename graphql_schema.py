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

# GraphQL Types


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
        students_data = get_all_students()
        # Convert dictionaries to Student objects
        return [
            Student(
                studentID=s["studentID"],
                firstName=s["firstName"],
                lastName=s["lastName"],
                age=s["age"],
                phoneNumber=s.get("phoneNumber"),
                email=s.get("email"),
                groupID=s["groupID"],
                guardians=s.get("guardians", [])
            )
            for s in students_data
        ]

    @strawberry.field
    def student(self, student_id: int) -> Optional[Student]:
        try:
            student_data = get_student_by_id(student_id)
        except HTTPException:
            return None
        
        # get_student_by_id returns raw DB row, need to format guardians
        guardians = []
        if student_data.get("guardian1ID"):
            # We'd need to fetch guardian names, but for now use empty list
            # Or we could call get_all_students and find the matching one
            pass
        
        # Try to get formatted student data from get_all_students
        all_students = get_all_students()
        formatted_student = next((s for s in all_students if s["studentID"] == student_id), None)
        
        if formatted_student:
            return Student(
                studentID=formatted_student["studentID"],
                firstName=formatted_student["firstName"],
                lastName=formatted_student["lastName"],
                age=formatted_student["age"],
                phoneNumber=formatted_student.get("phoneNumber"),
                email=formatted_student.get("email"),
                groupID=formatted_student["groupID"],
                guardians=formatted_student.get("guardians", [])
            )
        
        # Fallback to raw data
        return Student(
            studentID=student_data["studentID"],
            firstName=student_data["firstName"],
            lastName=student_data["lastName"],
            age=student_data["age"],
            phoneNumber=student_data.get("phoneNumber"),
            email=student_data.get("email"),
            groupID=student_data["groupID"],
            guardians=[]  # Can't get guardians from raw row easily
        )

    @strawberry.field
    def groups(self) -> List[SmallGroup]:
        groups_data = get_groups()
        # Convert dictionaries to SmallGroup objects
        result = []
        all_students = get_all_students()  # Get formatted students with guardians
        students_dict = {s["studentID"]: s for s in all_students}
        
        for g in groups_data:
            # Convert member dictionaries to Student objects
            members = []
            for m in g.get("members", []):
                student_id = m["studentID"]
                # Use formatted student data if available
                formatted_student = students_dict.get(student_id, m)
                members.append(Student(
                    studentID=formatted_student["studentID"],
                    firstName=formatted_student["firstName"],
                    lastName=formatted_student["lastName"],
                    age=formatted_student["age"],
                    phoneNumber=formatted_student.get("phoneNumber"),
                    email=formatted_student.get("email"),
                    groupID=formatted_student["groupID"],
                    guardians=formatted_student.get("guardians", [])
                ))
            result.append(SmallGroup(
                groupID=g["groupID"],
                name=g.get("name"),
                members=members
            ))
        return result

    @strawberry.field
    def events(self) -> List[Event]:
        events_data = get_all_events()
        # Convert dictionaries to Event objects
        return [
            Event(
                eventID=e["eventID"],
                name=e.get("name"),
                location=e["location"],
                date=e["date"],
                time=e["time"],
                customFields=e.get("customFields")
            )
            for e in events_data
        ]

    @strawberry.field
    def event(self, event_id: int) -> Optional[Event]:
        try:
            event_data = get_event_data(event_id)
        except HTTPException:
            return None
        # Convert dictionary to Event object
        return Event(
            eventID=event_data["eventID"],
            name=event_data.get("name"),
            location=event_data["location"],
            date=event_data["date"],
            time=event_data["time"],
            customFields=event_data.get("customFields")
        )

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
    def createEvent(
        self,
        name: str,
        location: str,
        date: str,
        time: str,
        customFields: Optional[JSON] = None
    ) -> Event:
        """Create a new event"""
        data = {
            "name": name,
            "location": location,
            "date": date,
            "time": time,
            "customFields": customFields or {}
        }
        event_data = create_event(data)
        # Convert dictionary to Event object
        return Event(
            eventID=event_data["eventID"],
            name=event_data.get("name"),
            location=event_data["location"],
            date=event_data["date"],
            time=event_data["time"],
            customFields=event_data.get("customFields")
        )

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