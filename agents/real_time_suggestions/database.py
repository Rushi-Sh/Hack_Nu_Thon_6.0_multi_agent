import os
from pymongo import MongoClient
from dotenv import load_dotenv
from bson import ObjectId  

# Load environment variables
load_dotenv()

# Connect to MongoDB
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DATABASE_NAME")]
collection = db[os.getenv("COLLECTION_NAME")]

def fetch_test_case_by_id(test_case_id):
    """Fetch a test case document by ID from MongoDB."""
    try:
        return collection.find_one({"_id": ObjectId(test_case_id)})
    except Exception as e:
        print(f"⚠️ Error fetching test case: {e}")
        return None
