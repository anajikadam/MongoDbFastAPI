import os
from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, EmailStr
from bson import ObjectId
from typing import Optional, List
import motor.motor_asyncio

app = FastAPI()

a1 = "anaji_091121"
p1 = "###########"
MONGODB_URL = "mongodb://{}:{}@cluster1-shard-00-00.zwyx0.mongodb.net:27017,cluster1-shard-00-01.zwyx0.mongodb.net:27017,cluster1-shard-00-02.zwyx0.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas-mualzv-shard-0&authSource=admin&retryWrites=true&w=majority".format(a1,p1)
# client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])

client = motor.motor_asyncio.AsyncIOMotorClient(MONGODB_URL)
# db = client.test
database = client.test
db = database['collection3']


class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

def student_helper(student) -> dict:
    return {
        "id": str(student["_id"]),
        "name": student["name"],
        "email": student["email"],
        "email": student["email"],
        "course": student["course"],
        "gpa": student["gpa"],
    }

class StudentModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(...)
    email: EmailStr = Field(...)
    course: str = Field(...)
    gpa: float = Field(...)

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }


class UpdateStudentModel(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]
    course: Optional[str]
    gpa: Optional[float]

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "Jane Doe",
                "email": "jdoe@example.com",
                "course": "Experiments, Science, and Fashion in Nanophotonics",
                "gpa": "3.0",
            }
        }


@app.post("/", response_description="Add new student", response_model=StudentModel)
async def create_student(student: StudentModel = Body(...)):
    student = jsonable_encoder(student)
    new_student = await db.insert_one(student)
    created_student = await db.find_one({"_id": new_student.inserted_id})
    return JSONResponse(status_code=status.HTTP_201_CREATED, content=created_student)


@app.get("/", response_description="List all students")
async def list_students():
    students = []
    async for student in db.find():
        students.append(student_helper(student))
    return students


@app.get("/{id}", response_description="Get a single student", response_model=StudentModel)
async def show_student(id: str):
    if (student := await db.find_one({"_id": id})) is not None:
        return student_helper(student)
    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@app.put("/{id}", response_description="Update a student", response_model=StudentModel)
async def update_student(id: str, student: UpdateStudentModel = Body(...)):
    student = {k: v for k, v in student.dict().items() if v is not None}

    if len(student) >= 1:
        update_result = await db.update_one({"_id": id}, {"$set": student})
        if update_result.modified_count == 1:
            if ( updated_student := await db.find_one({"_id": id}) ) is not None:
                return updated_student
                
    if (existing_student := await db.find_one({"_id": id})) is not None:
        return existing_student
    raise HTTPException(status_code=404, detail=f"Student {id} not found")


@app.delete("/{id}", response_description="Delete a student")
async def delete_student(id: str):
    delete_result = await db.delete_one({"_id": id})
    if delete_result.deleted_count == 1:
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT)
    raise HTTPException(status_code=404, detail=f"Student {id} not found")
