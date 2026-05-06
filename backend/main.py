from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware

import models, schemas
from database import engine, get_db
from auth import hash_password, verify_password, create_access_token

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://joyful-basbousa-86c009.netlify.app",
        "https://rainbow-bavarois-d59b54.netlify.app",
        "http://localhost:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # allow Netlify
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://stalwart-swan-0b2317.netlify.app",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

models.Base.metadata.create_all(bind=engine)


@app.post("/signup")
def signup(user: schemas.UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(models.User).filter(models.User.email == user.email).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    new_user = models.User(
        name=user.name,
        email=user.email,
        password=hash_password(user.password),
        role=user.role,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"message": "User registered successfully"}


@app.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()

    if not db_user or not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")

    token = create_access_token({
        "user_id": db_user.id,
        "email": db_user.email,
        "role": db_user.role,
    })

    return {
        "message": "Login successful",
        "access_token": token,
        "user_id": db_user.id,
        "name": db_user.name,
        "role": db_user.role,
    }


@app.get("/users")
def get_users(db: Session = Depends(get_db)):
    users = db.query(models.User).all()
    return users


@app.post("/projects")
def create_project(project: schemas.ProjectCreate, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.id == project.created_by).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    if user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admin can create projects")

    new_project = models.Project(
        name=project.name,
        created_by=project.created_by,
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)

    return {
        "message": "Project created",
        "project_id": new_project.id,
        "name": new_project.name,
    }


@app.get("/projects/{user_id}")
def get_projects(user_id: int, db: Session = Depends(get_db)):
    projects = db.query(models.Project).filter(models.Project.created_by == user_id).all()
    return projects


@app.put("/projects/{project_id}")
def update_project(project_id: int, project: schemas.ProjectUpdate, db: Session = Depends(get_db)):
    db_project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")

    db_project.name = project.name
    db.commit()
    db.refresh(db_project)

    return {"message": "Project updated", "project": db_project}


@app.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == project_id).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    db.query(models.Task).filter(models.Task.project_id == project_id).delete()
    db.delete(project)
    db.commit()

    return {"message": "Project deleted"}


@app.post("/tasks")
def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db)):
    project = db.query(models.Project).filter(models.Project.id == task.project_id).first()
    assigned_user = db.query(models.User).filter(models.User.id == task.assigned_to).first()

    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if not assigned_user:
        raise HTTPException(status_code=404, detail="Assigned user not found")

    new_task = models.Task(
        title=task.title,
        description=task.description,
        due_date=task.due_date,
        project_id=task.project_id,
        assigned_to=task.assigned_to,
        status="todo",
    )

    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return {"message": "Task created", "task_id": new_task.id}


@app.get("/tasks/{project_id}")
def get_tasks(project_id: int, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).filter(models.Task.project_id == project_id).all()
    return tasks


@app.get("/assigned-tasks/{user_id}")
def get_assigned_tasks(user_id: int, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).filter(models.Task.assigned_to == user_id).all()
    return tasks


@app.put("/tasks/{task_id}/status")
def update_task_status(task_id: int, status: str, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = status
    db.commit()
    db.refresh(task)

    return {"message": "Task status updated", "task": task}


@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: schemas.TaskUpdate, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.title = task_data.title
    task.description = task_data.description
    task.due_date = task_data.due_date

    db.commit()
    db.refresh(task)

    return {"message": "Task updated", "task": task}


@app.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()

    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(task)
    db.commit()

    return {"message": "Task deleted"}