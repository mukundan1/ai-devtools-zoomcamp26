from django.test import TestCase

# Create your tests here.
from datetime import date

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse

from .forms import GoalForm
from .models import Board, Category, Goal, Milestone, Task


class BoardModelTests(TestCase):
    def test_board_string_representation(self):
        board = Board.objects.create(title="2026 Goals")
        self.assertEqual(str(board), "2026 Goals")


class BoardViewTests(TestCase):
    def test_board_list_loads(self):
        response = self.client.get(reverse("board_list"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "visionboard/board_list.html")

    def test_create_board(self):
        response = self.client.post(
            reverse("board_create"),
            {
                "title": "Career Goals",
                "description": "Professional objectives",
            },
        )

        board = Board.objects.get(title="Career Goals")

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("board_detail", args=[board.id]))

    def test_board_detail_loads(self):
        board = Board.objects.create(title="Health Goals")

        response = self.client.get(reverse("board_detail", args=[board.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Health Goals")


class GoalTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(title="My Board")
        self.category = Category.objects.create(
            name="Career",
            color="#6366f1",
        )

    def test_create_goal(self):
        response = self.client.post(
            reverse("goal_create", args=[self.board.id]),
            {
                "title": "Learn Django",
                "description": "Build a complete Django project",
                "category": self.category.id,
                "deadline": "2026-12-31",
                "status": "in_progress",
                "progress_percent": 40,
            },
        )

        goal = Goal.objects.get(title="Learn Django")

        self.assertEqual(response.status_code, 302)
        self.assertEqual(goal.board, self.board)
        self.assertEqual(goal.progress_percent, 40)
        self.assertRedirects(
            response,
            reverse("board_detail", args=[self.board.id]),
        )

    def test_create_goal_with_image_url(self):
        response = self.client.post(
            reverse("goal_create", args=[self.board.id]),
            {
                "title": "Travel to Japan",
                "image_url": "https://example.com/japan.jpg",
                "status": "not_started",
                "progress_percent": 0,
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Goal.objects.filter(
                board=self.board,
                title="Travel to Japan",
                image_url="https://example.com/japan.jpg",
            ).exists()
        )

    def test_create_goal_with_uploaded_image(self):
        image = SimpleUploadedFile(
            "goal.jpg",
            b"fake-image-content",
            content_type="image/jpeg",
        )

        response = self.client.post(
            reverse("goal_create", args=[self.board.id]),
            {
                "title": "Run a marathon",
                "image": image,
                "status": "not_started",
                "progress_percent": 0,
            },
            format="multipart",
        )

        self.assertEqual(response.status_code, 302)

        goal = Goal.objects.get(title="Run a marathon")
        self.assertTrue(goal.image.name.startswith("goals/"))

    def test_edit_goal(self):
        goal = Goal.objects.create(
            board=self.board,
            title="Old title",
            progress_percent=10,
        )

        response = self.client.post(
            reverse("goal_edit", args=[goal.id]),
            {
                "title": "Updated title",
                "description": "Updated description",
                "status": "completed",
                "progress_percent": 100,
            },
        )

        goal.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(goal.title, "Updated title")
        self.assertEqual(goal.status, "completed")
        self.assertEqual(goal.progress_percent, 100)

    def test_goal_detail_loads(self):
        goal = Goal.objects.create(
            board=self.board,
            title="Read more books",
        )

        response = self.client.get(reverse("goal_detail", args=[goal.id]))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Read more books")

    def test_goal_position_is_saved(self):
        goal = Goal.objects.create(
            board=self.board,
            title="Build an app",
            position_x=40,
            position_y=40,
        )

        response = self.client.post(
            reverse("update_position", args=[goal.id]),
            {
                "x": 250,
                "y": 180,
            },
        )

        goal.refresh_from_db()

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content,
            {"success": True},
        )
        self.assertEqual(goal.position_x, 250)
        self.assertEqual(goal.position_y, 180)


class GoalFormTests(TestCase):
    def test_progress_cannot_exceed_100(self):
        form = GoalForm(
            data={
                "title": "Invalid goal",
                "status": "in_progress",
                "progress_percent": 101,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("progress_percent", form.errors)

    def test_progress_cannot_be_negative(self):
        form = GoalForm(
            data={
                "title": "Invalid goal",
                "status": "in_progress",
                "progress_percent": -1,
            }
        )

        self.assertFalse(form.is_valid())
        self.assertIn("progress_percent", form.errors)


class MilestoneAndTaskTests(TestCase):
    def setUp(self):
        self.board = Board.objects.create(title="Personal Goals")
        self.goal = Goal.objects.create(
            board=self.board,
            title="Improve fitness",
        )

    def test_add_milestone(self):
        response = self.client.post(
            reverse("goal_detail", args=[self.goal.id]),
            {
                "milestone_title": "Complete first training month",
                "title": "Complete first training month",
                "due_date": "2026-10-01",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Milestone.objects.filter(
                goal=self.goal,
                title="Complete first training month",
            ).exists()
        )

    def test_toggle_milestone(self):
        milestone = Milestone.objects.create(
            goal=self.goal,
            title="Run 5 kilometers",
        )

        response = self.client.post(
            reverse("toggle_milestone", args=[milestone.id])
        )

        milestone.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(milestone.completed)

    def test_add_task(self):
        response = self.client.post(
            reverse("goal_detail", args=[self.goal.id]),
            {
                "task_title": "Buy running shoes",
                "title": "Buy running shoes",
                "due_date": "2026-09-15",
            },
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Task.objects.filter(
                goal=self.goal,
                title="Buy running shoes",
            ).exists()
        )

    def test_toggle_task(self):
        task = Task.objects.create(
            goal=self.goal,
            title="Schedule training",
        )

        response = self.client.post(reverse("toggle_task", args=[task.id]))

        task.refresh_from_db()

        self.assertEqual(response.status_code, 302)
        self.assertTrue(task.completed)
