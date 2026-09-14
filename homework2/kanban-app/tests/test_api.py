def create_task(client, title="Test task", description="", status="todo"):
    response = client.post(
        "/api/tasks",
        json={
            "title": title,
            "description": description,
            "status": status,
        },
    )
    return response


def test_health_check(client):
    response = client.get("/api/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_openapi_contract_contains_task_endpoints(client):
    response = client.get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/api/health" in paths
    assert "/api/tasks" in paths
    assert "/api/tasks/{task_id}" in paths

    assert "get" in paths["/api/tasks"]
    assert "post" in paths["/api/tasks"]
    assert "patch" in paths["/api/tasks/{task_id}"]
    assert "delete" in paths["/api/tasks/{task_id}"]


def test_create_task(client):
    response = create_task(
        client,
        title="Write tests",
        description="Cover the API",
        status="todo",
    )

    assert response.status_code == 201

    task = response.json()

    assert task["id"] > 0
    assert task["title"] == "Write tests"
    assert task["description"] == "Cover the API"
    assert task["status"] == "todo"
    assert task["position"] == 0
    assert "created_at" in task


def test_list_tasks(client):
    create_task(client, title="First", status="todo")
    create_task(client, title="Second", status="doing")
    create_task(client, title="Third", status="done")

    response = client.get("/api/tasks")

    assert response.status_code == 200

    tasks = response.json()

    assert len(tasks) == 3
    assert {task["title"] for task in tasks} == {
        "First",
        "Second",
        "Third",
    }


def test_task_positions_increment_within_a_column(client):
    first = create_task(client, title="First", status="todo").json()
    second = create_task(client, title="Second", status="todo").json()
    third = create_task(client, title="Third", status="doing").json()

    assert first["position"] == 0
    assert second["position"] == 1
    assert third["position"] == 0


def test_update_task_fields(client):
    task = create_task(
        client,
        title="Original",
        description="Original description",
    ).json()

    response = client.patch(
        f"/api/tasks/{task['id']}",
        json={
            "title": "Updated",
            "description": "Updated description",
            "status": "doing",
            "position": 4,
        },
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["id"] == task["id"]
    assert updated["title"] == "Updated"
    assert updated["description"] == "Updated description"
    assert updated["status"] == "doing"
    assert updated["position"] == 4


def test_move_task_to_another_column_assigns_position(client):
    create_task(client, title="Existing", status="doing")
    task = create_task(client, title="Move me", status="todo").json()

    response = client.patch(
        f"/api/tasks/{task['id']}",
        json={"status": "doing"},
    )

    assert response.status_code == 200

    moved = response.json()

    assert moved["status"] == "doing"
    assert moved["position"] == 1


def test_delete_task(client):
    task = create_task(client, title="Delete me").json()

    response = client.delete(f"/api/tasks/{task['id']}")

    assert response.status_code == 204
    assert response.content == b""

    list_response = client.get("/api/tasks")

    assert list_response.status_code == 200
    assert list_response.json() == []


def test_missing_task_returns_404(client):
    response = client.patch(
        "/api/tasks/999999",
        json={"title": "Does not exist"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_delete_missing_task_returns_404(client):
    response = client.delete("/api/tasks/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"


def test_empty_title_is_rejected(client):
    response = create_task(client, title="")

    assert response.status_code == 422


def test_title_over_200_characters_is_rejected(client):
    response = create_task(client, title="x" * 201)

    assert response.status_code == 422


def test_description_over_2000_characters_is_rejected(client):
    response = create_task(client, description="x" * 2001)

    assert response.status_code == 422


def test_invalid_status_is_rejected(client):
    response = create_task(client, status="blocked")

    assert response.status_code == 422


def test_negative_position_is_rejected(client):
    task = create_task(client).json()

    response = client.patch(
        f"/api/tasks/{task['id']}",
        json={"position": -1},
    )

    assert response.status_code == 422


def test_partial_update_preserves_other_fields(client):
    task = create_task(
        client,
        title="Keep this title",
        description="Keep this description",
        status="todo",
    ).json()

    response = client.patch(
        f"/api/tasks/{task['id']}",
        json={"status": "done"},
    )

    assert response.status_code == 200

    updated = response.json()

    assert updated["title"] == "Keep this title"
    assert updated["description"] == "Keep this description"
    assert updated["status"] == "done"
