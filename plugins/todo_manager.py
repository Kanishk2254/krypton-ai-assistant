import re
import os
import json
from datetime import datetime

TODO_FILE = "data/todo.json"

if not os.path.exists("data"):
    os.makedirs("data")

if not os.path.exists(TODO_FILE):
    with open(TODO_FILE, "w") as f:
        json.dump([], f)

def load_todos():
    with open(TODO_FILE, "r") as f:
        return json.load(f)

def save_todos(todos):
    with open(TODO_FILE, "w") as f:
        json.dump(todos, f, indent=2)

def add_task(task):
    todos = load_todos()
    new_task = {"task": task, "done": False, "created": datetime.now().isoformat()}
    todos.append(new_task)
    save_todos(todos)
    speak(f"Added task: {task}")

def list_tasks():
    todos = load_todos()
    if not todos:
        speak("Your todo list is empty.")
        return
    speak("Here are your tasks.")
    for i, todo in enumerate(todos, 1):
        status = "✅ Done" if todo["done"] else "❌ Pending"
        speak(f"{i}. {todo['task']} - {status}")

def mark_task_done(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        todos[index]["done"] = True
        save_todos(todos)
        speak(f"Marked task {index + 1} as done.")
    else:
        speak("Invalid task number.")

def remove_task(index):
    todos = load_todos()
    if 0 <= index < len(todos):
        removed = todos.pop(index)
        save_todos(todos)
        speak(f"Removed task: {removed['task']}")
    else:
        speak("Invalid task number.")

# Parse input_text
text = input_text.lower()

if "add task" in text or "remember to" in text:
    match = re.search(r"(?:add task|remember to) (.+)", text)
    if match:
        task = match.group(1)
        add_task(task)
    else:
        speak("I couldn't understand the task to add.")

elif "list tasks" in text or "what are my tasks" in text:
    list_tasks()

elif "mark task" in text and "done" in text:
    match = re.search(r"mark task (\d+) done", text)
    if match:
        index = int(match.group(1)) - 1
        mark_task_done(index)
    else:
        speak("Please specify the task number to mark done.")

elif "remove task" in text:
    match = re.search(r"remove task (\d+)", text)
    if match:
        index = int(match.group(1)) - 1
        remove_task(index)
    else:
        speak("Please specify the task number to remove.")

else:
    speak("I couldn't understand your to-do command.")