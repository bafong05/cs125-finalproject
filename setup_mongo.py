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
    documents = [
        {
            "eventID": 1001,
            "customFields": {
                "packingList": ["sleeping bag", "water bottle", "Bible"],
                "bringFriend": True,
                "sessions": ["Morning Devotional", "Group Hike", "Campfire Worship"]
            }
        },
        {
            "eventID": 1002,
            "customFields": {
                "requiredItems": ["gloves", "closed-toe shoes"],
                "serviceHours": 4,
                "teamAssigned": "Blue Team"
            }
        },
        {
            "eventID": 1003,
            "customFields": {
                "foodPreference": "vegetarian-friendly",
                "gamesPlanned": ["Frisbee", "Water Balloon Toss"]
            }
        },
        {
            "eventID": 1004,
            "customFields": {
                "dressCode": "semi-formal",
                "mealChoice": ["chicken", "vegetarian"],
                "silentAuction": True
            }
        },
        {
            "eventID": 1005,
            "customFields": {
                "beachActivities": ["volleyball", "sandcastle contest"],
                "bringSunscreen": True
            }
        },
        {
            "eventID": 1006,
            "customFields": {
                "donationItems": ["canned food", "blankets"],
                "volunteersNeeded": 12
            }
        }
    ]

    print("Inserting event data...")
    collection.insert_many(documents)

    print("MongoDB setup complete.")

if __name__ == "__main__":
    setup_event_data()
