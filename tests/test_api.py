"""Integration tests for FastAPI task endpoints."""
def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["version"] == "2.0.0"

def test_create_and_read_task(client):
    task_payload = {
        "title": "Prepare final exam study notes",
        "description": "Chapter 4 to 8 summary",
        "priority": "high",
        "category": "study",
        "due": "2026-11-01",
        "recurrence": "none"
    }
    create_res = client.post("/api/v1/tasks/", json=task_payload)
    assert create_res.status_code == 201
    created_data = create_res.json()
    assert created_data["title"] == task_payload["title"]
    assert created_data["priority"] == "high"
    assert created_data["category"] == "study"
    assert created_data["done"] is False
    assert "uuid" in created_data
    task_id = created_data["id"]

    # Read single task
    read_res = client.get(f"/api/v1/tasks/{task_id}")
    assert read_res.status_code == 200
    assert read_res.json()["id"] == task_id

def test_toggle_task_done(client):
    task_payload = {"title": "Submit assignment", "priority": "urgent", "category": "study"}
    create_res = client.post("/api/v1/tasks/", json=task_payload)
    task_id = create_res.json()["id"]

    # Toggle to complete
    toggle_res1 = client.patch(f"/api/v1/tasks/{task_id}/toggle")
    assert toggle_res1.status_code == 200
    assert toggle_res1.json()["done"] is True
    assert toggle_res1.json()["status"] == "completed"

    # Toggle back to pending (undo)
    toggle_res2 = client.patch(f"/api/v1/tasks/{task_id}/toggle")
    assert toggle_res2.status_code == 200
    assert toggle_res2.json()["done"] is False
    assert toggle_res2.json()["status"] == "pending"

def test_filter_and_search_tasks(client):
    # Add multiple tasks
    client.post("/api/v1/tasks/", json={"title": "Math homework", "priority": "high", "category": "study"})
    client.post("/api/v1/tasks/", json={"title": "Client meeting", "priority": "medium", "category": "work"})
    client.post("/api/v1/tasks/", json={"title": "Grocery run", "priority": "low", "category": "personal"})

    # Search for math
    search_res = client.get("/api/v1/tasks/?search=math")
    assert search_res.status_code == 200
    assert len(search_res.json()) == 1
    assert search_res.json()[0]["title"] == "Math homework"

    # Filter by category work
    cat_res = client.get("/api/v1/tasks/?category=work")
    assert cat_res.status_code == 200
    assert len(cat_res.json()) == 1
    assert cat_res.json()[0]["title"] == "Client meeting"

    # Filter by priority high
    prio_res = client.get("/api/v1/tasks/?priority=high")
    assert prio_res.status_code == 200
    assert len(prio_res.json()) == 1

def test_soft_delete_task(client):
    create_res = client.post("/api/v1/tasks/", json={"title": "Clean desk", "priority": "low", "category": "personal"})
    task_id = create_res.json()["id"]

    # Soft delete (default)
    del_res = client.delete(f"/api/v1/tasks/{task_id}")
    assert del_res.status_code == 200

    # Active list should not contain it
    list_res = client.get("/api/v1/tasks/")
    assert len(list_res.json()) == 0

    # Archived list should contain it
    archived_res = client.get("/api/v1/tasks/?is_archived=true")
    assert len(archived_res.json()) == 1
    assert archived_res.json()[0]["id"] == task_id
