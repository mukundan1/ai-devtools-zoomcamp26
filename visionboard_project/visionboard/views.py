from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .forms import BoardForm, GoalForm, MilestoneForm, TaskForm
from .models import Board, Goal, Milestone, Task


def board_list(request):
    return render(request, "visionboard/board_list.html", {"boards": Board.objects.all()})


def board_create(request):
    form = BoardForm(request.POST or None)
    if form.is_valid():
        return redirect("board_detail", form.save().id)
    return render(request, "visionboard/form.html", {"form": form, "title": "New board"})


def board_detail(request, pk):
    board = get_object_or_404(Board, pk=pk)
    return render(request, "visionboard/board_detail.html", {"board": board})


def goal_create(request, board_id):
    board = get_object_or_404(Board, pk=board_id)
    form = GoalForm(request.POST or None, request.FILES or None)
    if form.is_valid():
        goal = form.save(commit=False)
        goal.board = board
        goal.save()
        return redirect("board_detail", board.id)
    return render(request, "visionboard/form.html", {"form": form, "title": "New goal"})


def goal_edit(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    form = GoalForm(request.POST or None, request.FILES or None, instance=goal)
    if form.is_valid():
        form.save()
        return redirect("goal_detail", goal.id)
    return render(request, "visionboard/form.html", {"form": form, "title": "Edit goal"})


def goal_detail(request, pk):
    goal = get_object_or_404(Goal, pk=pk)

    if request.method == "POST":
        if "milestone_title" in request.POST:
            form = MilestoneForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.goal = goal
                item.save()
        elif "task_title" in request.POST:
            form = TaskForm(request.POST)
            if form.is_valid():
                item = form.save(commit=False)
                item.goal = goal
                item.save()
        return redirect("goal_detail", goal.id)

    return render(
        request,
        "visionboard/goal_detail.html",
        {
            "goal": goal,
            "milestone_form": MilestoneForm(),
            "task_form": TaskForm(),
        },
    )


@require_POST
def update_position(request, pk):
    goal = get_object_or_404(Goal, pk=pk)
    goal.position_x = int(request.POST.get("x", goal.position_x))
    goal.position_y = int(request.POST.get("y", goal.position_y))
    goal.save(update_fields=["position_x", "position_y"])
    return JsonResponse({"success": True})


@require_POST
def toggle_milestone(request, pk):
    item = get_object_or_404(Milestone, pk=pk)
    item.completed = not item.completed
    item.save(update_fields=["completed"])
    return redirect("goal_detail", item.goal_id)


@require_POST
def toggle_task(request, pk):
    item = get_object_or_404(Task, pk=pk)
    item.completed = not item.completed
    item.save(update_fields=["completed"])
    return redirect("goal_detail", item.goal_id)
