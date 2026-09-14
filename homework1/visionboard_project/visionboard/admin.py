from django.contrib import admin
from .models import Board, Category, Goal, Milestone, Task

admin.site.register([Board, Category, Goal, Milestone, Task])
