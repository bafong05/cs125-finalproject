import mysql.connector
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.responses import FileResponse
import os
from contextlib import asynccontextmanager

# --- Import database connection functions ---
from database import get_db_connection, get_mongo_db, get_redis_conn, close_connections, get_mysql_pool, get_mongo_client, get_redis_client

# --- App Lifecycle Management ---
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize all database connections
    print("Application startup: Initializing database connections...")
    get_mysql_pool()
    get_mongo_client()
    get_redis_client()
    yield
    # Shutdown: Close all database connections
    print("Application shutdown: Closing database connections...")
    close_connections()

from fastapi.middleware.cors import CORSMiddleware

# --- FastAPI App ---
app = FastAPI(
    title="My Home Youth Group API",
    description="An API for interacting with the youth group data, using MySQL, MongoDB, and Redis.",
    version="1.0.0",
    lifespan=lifespan
)

# --- CORS Middleware ---
# This will allow the frontend (running on a different origin) to communicate with the API.
# For demonstration purposes, we allow all origins, methods, and headers.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to your frontend's domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Pydantic Models (for request/response validation) ---


# --- Pydantic Models for MongoDB Data ---
from typing import List, Optional, Any
from datetime import datetime
from pydantic import Field, GetCoreSchemaHandler
from pydantic_core import core_schema
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(
        cls, source: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """
        Return a Pydantic CoreSchema that defines how to validate and serialize ObjectIds.
        """
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema(
                [
                    core_schema.is_instance_schema(ObjectId),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ]
            ),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

    @classmethod
    def validate(cls, v: Any) -> ObjectId:
        """Validate that the input is a valid ObjectId."""
        if isinstance(v, ObjectId):
            return v
        if ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

class Review(BaseModel):
    customer_id: int
    rating: int
    comment: str
    tags: List[str]
    timestamp: datetime
    image_url: Optional[str] = None

class ProductReview(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    product_id: str
    reviews: List[Review]


# --- Pydantic Model for Redis Data ---



class Student(BaseModel):
    studentID: int
    firstName: str
    lastName: str
    age: int
    phoneNumber: str
    email: str
    guardian1ID: int
    guardian2ID: int
    groupID: int


class Attendance(BaseModel):
    studentID: int
    eventID: int
    checkInTime: datetime
    checkOutTime: datetime


class Event(BaseModel):
    eventID: int
    name: str
    location: str
    date: datetime
    time: datetime

# --- Pydantic Model for the Combined "Trifecta" Endpoint ---
class ProductOfTheDay(BaseModel):
    deal_details: DailyDeal
    reviews: Optional[ProductReview] = None

# --- API Endpoints ---
@app.get("/")
def read_root():
    """
    Root endpoint with a welcome message.
    """
    return {"message": "Welcome to the Youth Group API!"}

@app.get("/students", response_model=list[Student])
def get_all_students():
    """
    Retrieves a list of all students from MySQL.
    """
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, firstName, lastName FROM Student ORDER BY lastName, firstName;")
        students = cursor.fetchall()
        return students
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/customers/{customer_id}", response_model=Student)
def get_customer_by_id(customer_id: int):
    """
    Retrieves a specific customer by their ID from MySQL.
    """
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT studentID, firstName, lastName FROM Student WHERE id = %s;"
        cursor.execute(query, (customer_id,))
        student = cursor.fetchone()
        if not student:
            raise HTTPException(status_code=404, detail="Student not found")
        return student
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/products", response_model=list[Product])
def get_all_products():
    """
    Retrieves a list of all products from MySQL.
    """
    try:
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT id, flavor, kind, price FROM Product ORDER BY kind, flavor;")
        products = cursor.fetchall()
        return products
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"Database error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/products/{product_id}/reviews", response_model=ProductReview)
def get_product_reviews(product_id: str):
    """
    Retrieves all reviews for a specific product from MongoDB.
    """
    try:
        db = get_mongo_db()
        reviews_collection = db["product_reviews"]
        product_reviews = reviews_collection.find_one({"product_id": product_id})

        if not product_reviews:
            raise HTTPException(status_code=404, detail=f"No reviews found for product ID: {product_id}")

        return product_reviews
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

@app.get("/products/daily-deal", response_model=DailyDeal)
def get_daily_deal():
    """
    Retrieves the daily deal from Redis and MySQL.
    This demonstrates a caching pattern where Redis holds the deal ID
    and MySQL holds the full product details.
    """
    try:
        # 1. Fetch the deal from Redis
        r = get_redis_conn()
        deal_key = "current_event"
        deal_info = r.hgetall(deal_key)

        if not deal_info:
            raise HTTPException(status_code=404, detail="No daily deal found today!")

        product_id = deal_info['product_id']
        discount_percent = int(deal_info['discount_percent'])

        # 2. Fetch product details from MySQL
        cnx = get_db_connection()
        cursor = cnx.cursor(dictionary=True)
        query = "SELECT id, flavor, kind, price FROM Product WHERE id = %s;"
        cursor.execute(query, (product_id,))
        product_data = cursor.fetchone()

        if not product_data:
            raise HTTPException(status_code=404, detail=f"Daily deal product (ID: {product_id}) not found in database.")

        product = Product(**product_data)

        # 3. Combine and calculate the final price
        discounted_price = product.price * (1 - discount_percent / 100)

        return DailyDeal(
            product=product,
            discount_percent=discount_percent,
            discounted_price=round(discounted_price, 2),
            message=f"Today's deal: {discount_percent}% off {product.flavor} {product.kind}!"
        )

    except redis.RedisError as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")
    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail=f"MySQL error: {err}")
    finally:
        if 'cnx' in locals() and cnx.is_connected():
            cursor.close()
            cnx.close()

@app.get("/product-of-the-day-details", response_model=ProductOfTheDay)
def get_product_of_the_day():
    """
    **The Trifecta!**
    This endpoint orchestrates all three databases to build a complete response:
    1. Fetches the daily deal ID from **Redis**.
    2. Fetches the product details from **MySQL**.
    3. Fetches the product reviews from **MongoDB**.
    """
    try:
        # Step 1 & 2: Get the daily deal (from Redis and MySQL)
        # We can just call our existing endpoint function internally
        daily_deal_data = get_daily_deal()
        product_id = daily_deal_data.product.id

        # Step 3: Fetch reviews for that product from MongoDB
        reviews_data = None
        try:
            reviews_data = get_product_reviews(product_id)
        except HTTPException as e:
            # If no reviews are found (404), we don't want to fail the whole request.
            # We'll just proceed without review data.
            if e.status_code != 404:
                raise  # Re-raise if it's a different error

        # Step 4: Combine all data into the final response model
        return ProductOfTheDay(
            deal_details=daily_deal_data,
            reviews=reviews_data
        )

    except HTTPException as e:
        # Re-raise HTTP exceptions from the called functions
        raise e
    except Exception as e:
        # Catch any other unexpected errors
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/demo", response_class=FileResponse)
async def read_demo():
    """
    Serves the demo HTML page.
    """
    return os.path.join(os.path.dirname(__file__), "index.html")


if __name__ == "__main__":
    print("\nTo run this FastAPI application:")
    print("1. Make sure you have installed the required packages: pip install -r requirements.txt")
    print("2. Change directory into the 'python' folder: cd python")
    print("3. Run the server from within the 'python' folder: uvicorn main:app --reload --port 8099")
    print("4. Open your browser and go to http://127.0.0.1:8099/docs for the API documentation.")
    print("5. Open your browser and go to http://127.0.0.1:8099/demo for a UI demo.")
