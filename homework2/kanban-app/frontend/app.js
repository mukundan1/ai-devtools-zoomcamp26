const API = "/api";
const columns = [
  { id: "todo", title: "To do" },
  { id: "doing", title: "In progress" },
  { id: "done", title: "Done" },
];

let tasks = [];
let draggedTaskId = null;

const board = document.querySelector("#board");
const dialog = document.querySelector("#task-dialog");
const form = document.querySelector("#task-form");
const titleInput = document.querySelector("#title");
const descriptionInput = document.querySelector("#description");
const statusInput = document.querySelector("#status");

async function request(path, options = {}) {
  const response = await fetch(`${API}${path}`, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const body = await response.text();
    throw new Error(body || `Request failed: ${response.status}`);
  }

  return response.status === 204 ? null : response.json();
}

async function loadTasks() {
  tasks = await request("/tasks");
  render();
}

function render() {
  board.innerHTML = columns.map(column => {
    const columnTasks = tasks
      .filter(task => task.status === column.id)
      .sort((a, b) => a.position - b.position);

    return `
      <article class="column" data-status="${column.id}">
        <h2>
          ${column.title}
          <span class="count">${columnTasks.length}</span>
        </h2>
        <div class="task-list" data-status="${column.id}">
          ${
            columnTasks.length
              ? columnTasks.map(taskTemplate).join("")
              : `<div class="empty">Drop tasks here</div>`
          }
        </div>
      </article>
    `;
  }).join("");

  document.querySelectorAll(".task").forEach(card => {
    card.addEventListener("dragstart", () => {
      draggedTaskId = Number(card.dataset.id);
    });
  });

  document.querySelectorAll(".task-list").forEach(list => {
    list.addEventListener("dragover", event => event.preventDefault());

    list.addEventListener("drop", async event => {
      event.preventDefault();

      if (!draggedTaskId) return;

      const newStatus = list.dataset.status;
      const position = tasks.filter(task => task.status === newStatus).length;

      await request(`/tasks/${draggedTaskId}`, {
        method: "PATCH",
        body: JSON.stringify({
          status: newStatus,
          position,
        }),
      });

      draggedTaskId = null;
      await loadTasks();
    });
  });

  document.querySelectorAll("[data-delete]").forEach(button => {
    button.addEventListener("click", async () => {
      await request(`/tasks/${button.dataset.delete}`, {
        method: "DELETE",
      });
      await loadTasks();
    });
  });

  document.querySelectorAll("[data-edit]").forEach(button => {
    button.addEventListener("click", () => {
      const task = tasks.find(item => item.id === Number(button.dataset.edit));
      openDialog(task);
    });
  });
}

function taskTemplate(task) {
  return `
    <div class="task" draggable="true" data-id="${task.id}">
      <h3>${escapeHtml(task.title)}</h3>
      <p>${escapeHtml(task.description || "")}</p>
      <div class="task-footer">
        <button class="secondary" data-edit="${task.id}">Edit</button>
        <button data-delete="${task.id}">Delete</button>
      </div>
    </div>
  `;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function openDialog(task = null) {
  form.dataset.taskId = task?.id || "";
  document.querySelector("#dialog-title").textContent =
    task ? "Edit task" : "New task";

  titleInput.value = task?.title || "";
  descriptionInput.value = task?.description || "";
  statusInput.value = task?.status || "todo";

  dialog.showModal();
  titleInput.focus();
}

document.querySelector("#add-task").addEventListener("click", () => {
  openDialog();
});

document.querySelector("#cancel").addEventListener("click", () => {
  dialog.close();
});

form.addEventListener("submit", async event => {
  event.preventDefault();

  const taskId = form.dataset.taskId;
  const payload = {
    title: titleInput.value,
    description: descriptionInput.value,
    status: statusInput.value,
  };

  if (taskId) {
    await request(`/tasks/${taskId}`, {
      method: "PATCH",
      body: JSON.stringify(payload),
    });
  } else {
    await request("/tasks", {
      method: "POST",
      body: JSON.stringify(payload),
    });
  }

  dialog.close();
  await loadTasks();
});

loadTasks().catch(error => {
  board.innerHTML = `<div class="empty">Unable to load board: ${escapeHtml(error.message)}</div>`;
});
