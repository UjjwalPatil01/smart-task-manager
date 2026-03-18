import json
import os

FILE = "tasks.json"

def load_tasks():
    if not os.path.exists(FILE):
        return []

    try:
        with open(FILE, "r") as f:
            return json.load(f)
    except:
        return []

def save_tasks(tasks):
    with open(FILE, "w") as f:
        json.dump(tasks, f, indent=4)

def add_task():
    title = input("Enter task: ")
    due = input("Enter the Due Date (DD-MM-YYY): ")
    priority = input("Enter the Priority of Task(low/medium/high): ")
    if priority not in ["low", "medium", "high"]:
        priority = "low"
    tasks = load_tasks()
    tasks.append({"title": title, "done": False, "due": due, "priority": priority})
    save_tasks(tasks)
    print("Task added!")

def view_tasks():
    tasks = load_tasks()
    for i, task in enumerate(tasks):
        status = "✅" if task["done"] else "❌"
        if task["priority"] == "high":
            p = "🔥"
        elif task["priority"] == "medium":
            p = "⚡"
        else:
            p = "🟢"
        print(f"{i+1}. {task['title']} [{status}] {task['due']} {p}")

def mark_done():
    view_tasks()
    num = int(input("Enter task number: ")) - 1
    tasks = load_tasks()
    tasks[num]["done"] = True
    save_tasks(tasks)
    print("Task completed!")
    
def delete_task():
    view_tasks()
    num = int(input("Enter task number to delete: ")) - 1
    tasks = load_tasks()

    if 0 <= num < len(tasks):
        tasks.pop(num)
        save_tasks(tasks)
        print("Task deleted!")
    else:
        print("Invalid task number!")
        
def edit_task():
    view_tasks()
    num = int(input("Enter task number to edit: ")) - 1
    tasks = load_tasks()

    if 0 <= num < len(tasks):
        new_title = input("Enter new task name: ")
        tasks[num]["title"] = new_title
        save_tasks(tasks)
        print("Task updated!")
    else:
        print("Invalid task number!")

while True:
    print("\n1. Add Task\n2. View Tasks\n3. Mark Done\n4. Delete Task\n5. Edit Task\n6. Exit")
    choice = input("Choose: ")

    if choice == "1":
        add_task()
    elif choice == "2":
        view_tasks()
    elif choice == "3":
        mark_done()
    elif choice == "4":
        delete_task()
    elif choice == "5":
        edit_task()
    elif choice == "6":
        print("Exiting...")
        break