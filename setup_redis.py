from database import get_redis_conn, close_connections

def setup_redis_data():
    """
    Connects to Redis and sets up the 'daily_deal' hash with
    a product ID and a discount percentage.
    """
    try:
        r = get_redis_conn()

        # Define the daily deal data
        daily_deal_key = "daily_deal"
        deal_product_id = "50-CH"  # Chocolate Croissant
        deal_discount = 20  # 20% off

        # Use HSET to store the deal as a hash
        print(f"Setting up the daily deal in Redis for product: {deal_product_id}...")
        r.hset(daily_deal_key, mapping={
            "product_id": deal_product_id,
            "discount_percent": deal_discount
        })

        print("Daily deal setup successfully.")

        # Verify the data was set
        retrieved_deal = r.hgetall(daily_deal_key)
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
