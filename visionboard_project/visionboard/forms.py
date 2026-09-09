from django import forms
from .models import Board, Category, Goal, Milestone, Task


class BoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["title", "description"]


class GoalForm(forms.ModelForm):
    class Meta:
        model = Goal
        fields = [
            "title",
            "description",
            "category",
            "image",
            "image_url",
            "deadline",
            "status",
            "progress_percent",
        ]
        widgets = {
            "deadline": forms.DateInput(attrs={"type": "date"}),
            "progress_percent": forms.NumberInput(attrs={"min": 0, "max": 100}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ["title", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}


class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ["title", "due_date"]
        widgets = {"due_date": forms.DateInput(attrs={"type": "date"})}
