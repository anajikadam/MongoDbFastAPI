import motor.motor_asyncio

from bson.objectid import ObjectId

a1 = "anaji_091121"
p1 = "fjvhHGCPgAMY9nT6"
MONGODB_URL = "mongodb://{}:{}@cluster1-shard-00-00.zwyx0.mongodb.net:27017,cluster1-shard-00-01.zwyx0.mongodb.net:27017,cluster1-shard-00-02.zwyx0.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-mualzv-shard-0&authSource=admin&retryWrites=true&w=majority".format(a1,p1)

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)

database = client.test

student_collection = database['collection3']
# database.get_collection("students_collection")
# print(student_collection.find())
# helpers


def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "email": student["email"],
        "course": student["course"],
        "gpa": student["gpa"],
    }

# crud operations

# Retrieve all students present in the database
async def retrieve_students():
    students = []
    async for student in student_collection.find():
        students.append(student_helper(student))
    return students


# Add a new student into to the database
async def add_student(student_data: dict) -> dict:
    student = await student_collection.insert_one(student_data)
    new_student = await student_collection.find_one({"_id": student.inserted_id})
    return student_helper(new_student)


# Retrieve a student with a matching ID
async def retrieve_student(id: str) -> dict:
    student = await student_collection.find_one({"_id": ObjectId(id)})
    # print(id)
    if student:
        return student_helper(student)


# Update a student with a matching ID
async def update_student(id: str, data: dict):
    # Return false if an empty request body is sent.
    if len(data) < 1:
        return False
    student = await student_collection.find_one({"_id": ObjectId(id)})
    if student:
        updated_student = await student_collection.update_one(
            {"_id": ObjectId(id)}, {"$set": data}
        )
        if updated_student:
            return True
        return False


# Delete a student from the database
async def delete_student(id: str):
    student = await student_collection.find_one({"_id": ObjectId(id)})
    if student:
        await student_collection.delete_one({"_id": ObjectId(id)})
        return True
