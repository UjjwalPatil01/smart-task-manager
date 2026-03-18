from flask import Flask, render_template, request, redirect
import json
import os

app = Flask(__name__)
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


@app.route("/")
def index():
    tasks = load_tasks()

    # GET PARAMETERS
    filter_type = request.args.get("filter", "all")
    sort = request.args.get("sort")
    order = request.args.get("order", "asc")
    priority_filter = request.args.get("priority")
    search = request.args.get("search")

    # FILTER STATUS
    if filter_type == "pending":
        tasks = [t for t in tasks if not t["done"]]
    elif filter_type == "done":
        tasks = [t for t in tasks if t["done"]]

    # FILTER PRIORITY
    if priority_filter:
        tasks = [t for t in tasks if t["priority"] == priority_filter]

    # SEARCH
    if search:
        tasks = [t for t in tasks if search.lower() in t["title"].lower()]

    # SORT
    if sort == "due":
        tasks.sort(key=lambda x: x["due"] or "")
    elif sort == "priority":
        priority_order = {"high": 1, "medium": 2, "low": 3}
        tasks.sort(key=lambda x: priority_order.get(x["priority"], 3))

    # ASC / DESC
    if order == "desc":
        tasks.reverse()

    # STATS
    total = len(tasks)
    done = len([t for t in tasks if t["done"]])
    pending = total - done

    return render_template(
    "index.html",
    tasks=tasks,
    total=total,
    done=done,
    pending=pending,
    filter_type=filter_type,
    sort=sort,
    order=order,
    priority_filter=priority_filter,
    search=search
)


@app.route("/add", methods=["POST"])
def add():
    title = request.form.get("title")
    due = request.form.get("due")
    priority = request.form.get("priority")

    if priority not in ["low", "medium", "high"]:
        priority = "low"

    tasks = load_tasks()
    tasks.append({
        "title": title,
        "done": False,
        "due": due,
        "priority": priority
    })

    save_tasks(tasks)
    return redirect("/")


@app.route("/done/<int:index>")
def mark_done(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        if not tasks[index]["done"]:
            tasks[index]["done"] = True
            save_tasks(tasks)
    return redirect("/")


@app.route("/delete/<int:index>")
def delete(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks.pop(index)
        save_tasks(tasks)
    return redirect("/")


@app.route("/edit/<int:index>")
def edit(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        return render_template("edit.html", task=tasks[index], index=index)
    return redirect("/")


@app.route("/update/<int:index>", methods=["POST"])
def update(index):
    tasks = load_tasks()
    if 0 <= index < len(tasks):
        tasks[index]["title"] = request.form.get("title")
        tasks[index]["due"] = request.form.get("due")
        tasks[index]["priority"] = request.form.get("priority")
        save_tasks(tasks)
    return redirect("/")


if __name__ == "__main__":
    app.run(debug=True)