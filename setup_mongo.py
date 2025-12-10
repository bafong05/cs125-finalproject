from pymongo import MongoClient
import os

def setup_event_data():
    mongo_client = MongoClient(
        os.getenv("MONGO_URL"),
        tls=True,
        tlsAllowInvalidCertificates=True
    )
    mongo_db = mongo_client["youth_group"]
    collection = mongo_db["event_data"]

    # Clear existing event data
    print("Clearing existing event data")
    collection.delete_many({})

    # Sample custom event data
    # Note: eventIDs must match the eventIDs in MySQL (data.sql)
    # MySQL events have IDs: 1, 2, 3, 4, 5, 6
    documents = [
        {
            "eventID": 1,
            "customFields": {
                "packingList": ["sleeping bag", "water bottle", "Bible"],
                "bringFriend": True,
                "sessions": ["Morning Devotional", "Group Hike", "Campfire Worship"]
            }
        },
        {
            "eventID": 2,
            "customFields": {
                "requiredItems": ["gloves", "closed-toe shoes"],
                "serviceHours": 4,
                "teamAssigned": "Blue Team"
            }
        },
        {
            "eventID": 3,
            "customFields": {
                "foodPreference": "vegetarian-friendly",
                "gamesPlanned": ["Frisbee", "Water Balloon Toss"]
            }
        },
        {
            "eventID": 4,
            "customFields": {
                "dressCode": "semi-formal",
                "mealChoice": ["chicken", "vegetarian"],
                "silentAuction": True
            }
        },
        {
            "eventID": 5,
            "customFields": {
                "beachActivities": ["volleyball", "sandcastle contest"],
                "bringSunscreen": True
            }
        },
        {
            "eventID": 6,
            "customFields": {
                "donationItems": ["canned food", "blankets"]
            }
        }
    ]

    print("Inserting event data...")
    collection.insert_many(documents)

    print("MongoDB setup complete.")

if __name__ == "__main__":
    setup_event_data()
