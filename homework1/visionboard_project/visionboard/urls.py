from django.urls import path
from . import views

urlpatterns = [
    path("", views.board_list, name="board_list"),
    path("boards/new/", views.board_create, name="board_create"),
    path("boards/<int:pk>/", views.board_detail, name="board_detail"),
    path("boards/<int:board_id>/goals/new/", views.goal_create, name="goal_create"),
    path("goals/<int:pk>/", views.goal_detail, name="goal_detail"),
    path("goals/<int:pk>/edit/", views.goal_edit, name="goal_edit"),
    path("goals/<int:pk>/position/", views.update_position, name="update_position"),
    path("milestones/<int:pk>/toggle/", views.toggle_milestone, name="toggle_milestone"),
    path("tasks/<int:pk>/toggle/", views.toggle_task, name="toggle_task"),
]
