# These commands are the Python equivalent of the MongoDB commands.
# If a client calls an API endpoint with a new event type name, then this command would be used.
db.eventTypes.insert_one(doc)

# However, if there are changes to the format of the type of event, this command would be used.
db.eventTypes.update_one({"typeId": type_id}, {"$set": updates})

# When specific events of that type are being created, then MySQL is used to create the base event record,
# which likely involves calling the CREATE TABLE Event statement to get basic columns like eventID, among other things.
# The client then sends a payload with values that were inputted in, which we need to store in MongoDB, and is likely
# done by db.eventCustomData.insert_one(doc), and it's tied to the primary key in MySQL.





























# Each command is the Python equivalent of its respective Redis command.
# The first one checks a student into an event.
r.sadd(f"event:{eventID}:checkedIn", studentID)

# This one checks a student out of an event.
r.srem(f"event:{eventID}:checkedIn", studentID)

# If the administrator is querying Redis, these commands would be used
# to see who is checked in and how many people are checked in at that time.

# This shows everyone that is currently checked in.
r.smembers(f"event:{eventID}:checkedIn")

# This shows the total amount of people that are currently checked in.
r.scard(f"event:{eventID}:checkedIn")

# When the event ends, there are a couple of necessary commands that need to be used to record final data.

# We run the members command again to show everyone that checked in throughout the event.
r.smembers(f"event:{eventID}:checkedIn")

# The result of this command needs to be inputted into MySQL, since it's the attendance that will be saved for later.


# This command gets rid of the Redis keys once the event ends so they don't take up unnecessary space.
r.delete(f"event:{eventID}:checkedIn")