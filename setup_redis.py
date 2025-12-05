from database import get_redis_conn, close_connections

def setup_redis_data():
    """
    Connects to Redis and sets up the 'current_event' hash with
    an event ID and a discount percentage.
    """
    try:
        r = get_redis_conn()

        # Define the event data
        current_event_key = "current_event"
        event_id = 1001  # Winter Retreat
        deal_discount = 20  # 20% off

        # Use HSET to store the deal as a hash
        print(f"Setting up the current event attendance in Redis for event: {event_id}...")
        r.hset(current_event_key, mapping={
            "event_id": event_id,
            "discount_percent": deal_discount
        })

        print("Current event attendance setup successfully.")

        # Verify the data was set
        retrieved_deal = r.hgetall(current_event_key)
        print(f"Verified data from Redis: {retrieved_deal}")

    except Exception as e:
        print(f"An error occurred during Redis setup: {e}")
    finally:
        # No explicit close needed for this library version in this context
        close_connections()

if __name__ == "__main__":
    print("--- Starting Redis Data Setup ---")
    setup_redis_data()
    print("--- Redis Data Setup Finished ---")
