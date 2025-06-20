"""
CRM (Customer Relationship Management) tools for MCP server
"""
import os
import uuid
from typing import Dict, List, Any, Optional
from pymongo import MongoClient
from dotenv import load_dotenv
import logging
from config import MONGO_URI, MONGO_DB, MONGO_COLLECTION

# Configure logging
logger = logging.getLogger("crm_tools")

# Initialize MongoDB connection
def init_mongodb():
    """Initialize MongoDB connection"""
    try:

        # print(f"Connecting to MongoDB at {mongo_uri}, database: {mongo_db}, collection: {mongo_collection}")
        
        # Create connection
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB]
        collection = db[MONGO_COLLECTION]
        
        # Create unique index on "id" field
        collection.create_index("id", unique=True)
        
        logger.info(f"MongoDB initialized: {MONGO_DB}.{MONGO_COLLECTION}")
        
        return collection
    except Exception as e:
        logger.error(f"Failed to initialize MongoDB: {e}")
        # Return None to indicate failure
        return None

# Try to initialize MongoDB
try:
    customer_collection = init_mongodb()
except Exception as e:
    logger.warning(f"Using in-memory customer storage due to MongoDB initialization error: {e}")
    customer_collection = None

# Fallback to in-memory storage if MongoDB is not available
customers_memory = {}

def register_crm_tools(mcp):
    """Register CRM tools with the MCP server"""
    
    @mcp.tool
    def get_customer(customer_id: str) -> Dict[str, Any]:
        """
        Retrieve customer information by ID
        
        Args:
            customer_id: The unique ID of the customer
            
        Returns:
            Customer information or error message
        """
        try:
            if customer_collection:
                # Use MongoDB
                customer = customer_collection.find_one({"id": customer_id}, {"_id": 0})
                if customer:
                    return customer
                else:
                    return {"error": "Customer not found", "status": "error"}
            else:
                # Use in-memory storage
                if customer_id in customers_memory:
                    return customers_memory[customer_id]
                else:
                    return {"error": "Customer not found", "status": "error"}
        except Exception as e:
            logger.error(f"Error retrieving customer: {e}")
            return {"error": str(e), "status": "error"}
    
    @mcp.tool
    def create_customer(name: str, email: str, phone: str = "") -> Dict[str, Any]:
        """
        Create a new customer record
        
        Args:
            name: Customer name
            email: Customer email address
            phone: Customer phone number (optional)
            
        Returns:
            Newly created customer record
        """
        try:
            # Generate unique ID
            customer_id = str(uuid.uuid4())
            
            # Create customer object
            customer = {
                "id": customer_id,
                "name": name,
                "email": email,
                "phone": phone
            }
            
            if customer_collection is not None:
                # Use MongoDB
                customer_collection.insert_one(customer)
            else:
                # Use in-memory storage
                customers_memory[customer_id] = customer
                
            return customer
        except Exception as e:
            logger.error(f"Error creating customer: {e}")
            return {"error": str(e), "status": "error"}
    
    @mcp.tool
    def update_customer(customer_id: str, name: Optional[str] = None, 
                       email: Optional[str] = None, phone: Optional[str] = None) -> Dict[str, Any]:
        """
        Update customer information
        
        Args:
            customer_id: The unique ID of the customer
            name: Updated name (optional)
            email: Updated email (optional)
            phone: Updated phone (optional)
            
        Returns:
            Updated customer record
        """
        try:
            # Create update dictionary with only provided fields
            updates = {}
            if name is not None:
                updates["name"] = name
            if email is not None:
                updates["email"] = email
            if phone is not None:
                updates["phone"] = phone
                
            if not updates:
                return {"error": "No update fields provided", "status": "error"}
                
            if customer_collection:
                # Use MongoDB
                result = customer_collection.update_one(
                    {"id": customer_id}, 
                    {"$set": updates}
                )
                
                if result.matched_count == 0:
                    return {"error": "Customer not found", "status": "error"}
                    
                # Return updated customer
                return get_customer(customer_id)
            else:
                # Use in-memory storage
                if customer_id not in customers_memory:
                    return {"error": "Customer not found", "status": "error"}
                    
                # Update customer
                customers_memory[customer_id].update(updates)
                
                # Return updated customer
                return customers_memory[customer_id]
        except Exception as e:
            logger.error(f"Error updating customer: {e}")
            return {"error": str(e), "status": "error"}
    
    @mcp.tool
    def list_customers(limit: int = 10) -> Dict[str, Any]:
        """
        List customers
        
        Args:
            limit: Maximum number of customers to return
            
        Returns:
            List of customers
        """
        try:
            if customer_collection:
                # Use MongoDB
                customers = list(customer_collection.find({}, {"_id": 0}).limit(limit))
                return {
                    "customers": customers,
                    "count": len(customers),
                    "status": "success"
                }
            else:
                # Use in-memory storage
                customers = list(customers_memory.values())[:limit]
                return {
                    "customers": customers,
                    "count": len(customers),
                    "status": "success"
                }
        except Exception as e:
            logger.error(f"Error listing customers: {e}")
            return {"error": str(e), "status": "error"}
