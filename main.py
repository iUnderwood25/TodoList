from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import psycopg2
from psycopg2.extras import RealDictCursor
import os  

app = FastAPI()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "tasks_db")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "Sal373!!@&man!!")

class Task(BaseModel):
    NumberOfTask: int
    task: str
    is_done: bool = False

def get_connection():
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
    return conn

@app.on_event("startup")
def setup():
    try:
        conn = psycopg2.connect(host=DB_HOST, database="postgres", user=DB_USER, password=DB_PASSWORD)
        conn.autocommit = True  
        conn.cursor().execute("CREATE DATABASE tasks_db")
        conn.close()
    except:
        pass
    
    try:
        conn = get_connection()
        conn.cursor().execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                NumberOfTask INTEGER PRIMARY KEY,
                task TEXT NOT NULL,
                is_done BOOLEAN DEFAULT FALSE
            )
        """)
        conn.commit()
        conn.close()
    except:
        pass

@app.get("/tasks")
def get_tasks():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks")
    tasks = cursor.fetchall()
    conn.close()
    return tasks

@app.post("/tasks")
def add_task(task: Task):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks WHERE NumberOfTask = %s", (task.NumberOfTask,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail="المهمة موجودة من قبل")

    cursor.execute("INSERT INTO tasks VALUES (%s, %s, %s)", 
                   (task.NumberOfTask, task.task, task.is_done))
    conn.commit()
    conn.close()
    return task

@app.delete("/tasks/{task_number}")
def delete_task(task_number: int):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE NumberOfTask = %s", (task_number,))

    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=404, detail="المهمة غير موجودة")

    conn.commit()
    conn.close()
    return {"message": "تم حذف المهمة"}
