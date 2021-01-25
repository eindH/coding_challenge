from typing import Optional
from fastapi import FastAPI
import pymongo
from fastapi.testclient import TestClient
from pydantic import BaseModel
from bson.objectid import ObjectId

client = pymongo.MongoClient(
    "mongodb+srv://admin:adminPassword@cluster0.ldmkj.mongodb.net/propertyManager?retryWrites=true&w=majority"
)
db = client.propertyManager
userCol = db.Users
propertyCol = db.Properties
app = FastAPI()


class User(BaseModel):
    # DEFINES A USER MODEL
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class Property(BaseModel):
    # DEFINES A PROPERTY MODEL
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    postcode: Optional[str] = None
    value: Optional[int] = None
    owner: Optional[str] = None


@app.get("/")
def index():
    return {"message": "Welcome to the property management platform!"}


@app.post('/reg-user')
async def regUser(user: User):
    # REGISTER USER BY ENTERING FIRST AND LAST NAME
    new_user = userCol.insert_one(
        {
            'first_name': user.first_name,
            'last_name': user.last_name
        })
    return {
        "message": user.first_name + ' ' +
        user.last_name + ' ADDED WITH ID# ' +
        str(new_user.inserted_id)
    }


@app.get('/list-all-users')
async def listAllUsers():
    # GET CURSOR FOR COLLECTION AND LOOP THRU. RETURN ALL USERS IN DATABASE
    cursor = userCol.find({})
    user_dict = {}
    for doc in cursor:
        user_dict[str(doc['_id'])] = {
            'first_name': doc['first_name'],
            'last_name': doc['last_name']
        }
    return user_dict


@app.get('/user-by-id/{user_id}')
async def userById(user_id):
    # SEARCHES MONGODB BY USERID AND RETURNS USER DOCUMENT
    user_details = userCol.find_one({"_id": ObjectId(str(user_id))})
    return {
        'first_name': user_details['first_name'],
        'last_name': user_details['last_name']
    }


@app.post('/create-property')
async def createProperty(property_doc: Property):
    # INSERTS NEW PROPERTY DOCUMENT INTO MONGODB
    new_property = propertyCol.insert_one(
        {
            'address1': property_doc.address1,
            'address2': property_doc.address2,
            'city': property_doc.city,
            'postcode': property_doc.postcode,
            'value': property_doc.value,
            'owner': property_doc.owner
        })
    return {
        "message": "PROPERTY ADDED WITH ID#" + str(new_property.inserted_id)
    }


@app.get('/find-user-properties/{user_id}')
async def findUserProperties(user_id):
    # CREATES CURSOR AND ITERATES THRU ALL OWNER PROPERTIES
    cursor = propertyCol.find({'owner': user_id})
    property_dict = {}
    for doc in cursor:
        property_dict[str(doc['_id'])] = {
            'address1': doc['address1'],
            'address2': doc['address2'],
            'city': doc['city'],
            'postcode': doc['postcode'],
            'value': doc['value'],
            'owner': doc['owner']
        }
    return property_dict


@app.post('/update-user/{user_id}')
async def updateUser(user_id, updated_details: User):
    # TAKES PREV DETAILS AND CHANGES IF UPDATED, LEAVE THE SAME IF NOT
    user = userCol.find_one({"_id": ObjectId(str(user_id))})
    update_first_name = user['first_name']
    update_last_name = user['last_name']
    if updated_details.first_name:
        update_first_name = updated_details.first_name
    if updated_details.last_name:
        update_last_name = updated_details.last_name
    userCol.find_one_and_update({
        "_id": ObjectId(str(user_id))},
        {
            "$set":
            {
                'first_name': update_first_name,
                'last_name': update_last_name
            }
        })
    return {"message": "UPDATED USER"}


@app.post('/update-property/{property_id}')
async def updateProperty(property_id, updated_details: Property):
    # TAKES PREV DETAILS AND CHANGES IF UPDATED
    property_doc = propertyCol.find_one({"_id": ObjectId(str(property_id))})
    update_address1 = property_doc['address1']
    update_address2 = property_doc['address2']
    update_city = property_doc['city']
    update_postcode = property_doc['postcode']
    update_value = property_doc['value']
    if updated_details.address1:
        update_address1 = updated_details.address1
    if updated_details.address2:
        update_address2 = updated_details.address2
    if updated_details.city:
        update_city = updated_details.city
    if updated_details.postcode:
        update_postcode = updated_details.postcode
    if updated_details.value:
        update_value = updated_details.value
    propertyCol.find_one_and_update({
        "_id": ObjectId(str(property_id))},
        {
            "$set":
            {
                'address1': update_address1,
                'address2': update_address2,
                'city': update_city,
                'postcode': update_postcode,
                'value': update_value,
                'owner': property_doc['owner']
            }
        })
    return {"message": "PROPERTY UPDATED"}


@app.post('/update-property-owner/{property_id}')
async def updatePropertyOwner(property_id, updated_details: Property):
    # TAKES PREV OWNER AND CHANGES TO UPDATED
    property_doc = propertyCol.find_one({"_id": ObjectId(str(property_id))})
    update_owner = property_doc['owner']
    if updated_details.owner:
        update_owner = updated_details.owner
    propertyCol.find_one_and_update({
        "_id": ObjectId(str(property_id))
    }, {
        "$set":
        {'owner': update_owner}
    })
    return {"message": "PROPERTY OWNER UPDATED"}


@app.post('/delete-property/{property_id}')
async def deletePropertyCommand(property_id):
    # DELETE PROPERTY BY ID
    propertyCol.find_one_and_delete({"_id": ObjectId(str(property_id))})
    return {"message": "PROPERTY DELETED"}


@app.post('/delete-user/{user_id}')
async def deleteUser(user_id):
    # DELETE ALL OWNER PROPERTIES BEFORE DELETING OWNER
    propertyCol.delete_many({'owner': user_id})
    userCol.delete_one({"_id": ObjectId(str(user_id))})
    return {"message": "USER AND PROPERTIES DELETED"}

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {
        "message": "Welcome to the property management platform!"
    }


def test_find_user_properties():
    response = client.get("/find-user-properties/600f04db5d3f93364db1d2e5")
    assert response.status_code == 200
    assert response.json() == {
        "600f05d35d3f93364db1d2e7": {
            "address1": "Palais de l'Elysee",
            "address2": "55 Rue du Faubourg",
            "city": "PARIS",
            "postcode": "75008",
            "value": 130000000,
            "owner": "600f04db5d3f93364db1d2e5"
        }, "600f06a75d3f93364db1d2e8": {
            "address1": "Arc de Triomphe",
            "address2": "Place Charles de Gaulle",
            "city": "PARIS",
            "postcode": "75008",
            "value": 130000000,
            "owner": "600f04db5d3f93364db1d2e5"
        }
    }


def test_find_user_by_id():
    response = client.get("/user-by-id/600f04db5d3f93364db1d2e5")
    assert response.status_code == 200
    assert response.json() == {
        "first_name": "Napoleon", "last_name": "Bonaparte"
    }
