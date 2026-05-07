# Team Task Manager (Full-Stack)

A full-stack web application to manage projects, assign tasks, and track progress with role-based access control (Admin/Member).

## Live Demo
(Add your deployed URL here after deployment)

## Features

- Authentication (Signup / Login)
- Role-based access (Admin / Member)
- Project management
- Task creation and assignment
- Task status tracking (Todo, In Progress, Done)
- Dashboard with:
  - Total tasks
  - Completed tasks
  - Pending tasks
  - Overdue tasks

## Tech Stack

Frontend:
- React.js
- CSS

Backend:
- FastAPI
- SQLAlchemy

Database:
- SQLite

## API Endpoints

- POST /signup → Register user
- POST /login → Login user
- POST /projects → Create project
- GET /projects → Get all projects
- POST /tasks → Create task
- GET /tasks/{project_id} → Get tasks
- PUT /tasks/{task_id} → Update task status
- DELETE /tasks/{task_id} → Delete task

## Role-Based Flow

Admin:
- Create projects
- Create tasks
- Assign tasks to members

Member:
- View assigned tasks
- Update task status

## Setup Instructions

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload
