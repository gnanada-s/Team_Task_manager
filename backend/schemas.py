from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class ProjectCreate(BaseModel):
    name: str
    created_by: int

class ProjectUpdate(BaseModel):
    name: str

class TaskCreate(BaseModel):
    title: str
    description: str
    due_date: str
    project_id: int
    assigned_to: int

class TaskUpdate(BaseModel):
    title: str
    description: str
    due_date: str
    