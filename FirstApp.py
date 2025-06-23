from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List

app = FastAPI()

class Task(BaseModel):
    NumberOfTask: int
    task: str
    is_done: bool = False

tasks: List[Task] = []

@app.get("/tasks/api", response_model=List[Task])
def get_tasks():
    return tasks

@app.post("/tasks/api/a", response_model=Task)
def add_task(task: Task):
    for t in tasks:
        if t.NumberOfTask == task.NumberOfTask:
            raise HTTPException(status_code=400, detail="المهمة موجودة قبل")
    tasks.append(task)
    return task


@app.delete("/tasks/api/un/{task_number}") 
def delete_task(task_number: int):
    for i, t in enumerate(tasks):
        if t.NumberOfTask == task_number:
            tasks.pop(i)
            return {"message": "Removed"}
    raise HTTPException(status_code=404, detail="The task not found")