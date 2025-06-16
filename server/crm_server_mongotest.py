import os
from dotenv import load_dotenv
from pymongo import MongoClient
import uuid
from fastmcp import FastMCP

# Load environment variables from .env file
load_dotenv()

# Get MongoDB connection details from environment variables
mongo_uri = os.getenv('MONGO_URI')
mongo_db = os.getenv('MONGO_DB')
mongo_collection = os.getenv('MONGO_COLLECTION')

# Create MongoClient instance
client = MongoClient(mongo_uri)

# Select database and collection
db = client[mongo_db]
collection = db[mongo_collection]

# Create unique index on "id" field
collection.create_index("id", unique=True)

# Create FastMCP server
mcp = FastMCP(name="CRM Server")

# Define tool to retrieve customer by ID
@mcp.tool()
def get_customer(customer_id: str) -> dict:
    """Retrieve customer information by ID"""
    customer = collection.find_one({"id": customer_id}, {"_id": 0})
    if customer:
        return customer
    else:
        return {"error": "Customer not found"}

# Define tool to create a new customer
@mcp.tool()
def create_customer(name: str, email: str, phone: str) -> dict:
    """Create a new customer record"""
    customer_id = str(uuid.uuid4())
    customer = {
        "id": customer_id,
        "name": name,
        "email": email,
        "phone": phone
    }
    collection.insert_one(customer)
    return customer

# Run the server
if __name__ == "__main__":
    mcp.run()