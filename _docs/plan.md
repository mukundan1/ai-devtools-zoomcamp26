# Vision Board Tool — Implementation Plan

## 1. Product scope

Build a single-user Django web application for creating and managing multiple digital vision boards.

Each board contains movable visual goal cards. Each goal can include:

- Title
- Description
- Category
- Uploaded image or external image URL
- Deadline
- Progress percentage
- Status: Not started, In progress, Completed
- Milestones
- Tasks

The application uses Django server-rendered templates with HTML, CSS, and minimal JavaScript.

## 2. Explicitly out of scope

- User accounts and authentication
- Collaboration and sharing
- Public boards
- Social features
- Habit tracking
- Notifications and reminders
- Mobile application
- Advanced image editing
- Drag-and-drop file uploads

## 3. Main user workflows

### Create a board

1. User opens the boards page.
2. User creates a board with a title and optional description.
3. The new board appears in the board list.

### Add a goal

1. User opens a board.
2. User selects “Add goal.”
3. User enters goal details and optional image.
4. The goal appears as a card on the board.

### Arrange a board

1. User drags goal cards around the board.
2. The application saves each card’s position.
3. The layout is restored when the board is reopened.

### Manage progress

1. User opens a goal card or detail page.
2. User updates status, percentage, deadline, milestones, or tasks.
3. The updated progress is displayed on the board.

## 4. Suggested Django structure

```text
project/
├── manage.py
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── visionboard/
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── forms.py
│   ├── admin.py
│   ├── migrations/
│   └── templates/visionboard/
│       ├── board\_list.html
│       ├── board\_detail.html
│       ├── board\_form.html
│       ├── goal\_detail.html
│       └── goal\_form.html
├── static/
│   ├── css/
│   └── js/
└── media/
