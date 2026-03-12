# Lab: Building EduFinApp — A Step-by-Step Guide

## What You Will Build

By the end of this lab, you will have built **EduFinApp** — a Django REST API project from scratch. You will understand:
- How Django projects and apps are structured
- Why we use a **Custom User Model** (and why you should *always* start with one)
- How Django **Models** map Python classes to database tables
- How **Serializers** convert complex data (like database records) into JSON
- How **Views** handle HTTP requests and return responses
- How **URLs** route incoming requests to the correct view

> **Who is this for?** Absolute beginners to Django and Django REST Framework (DRF). If you've written basic Python and understand what an API is, you're ready.

---

## Prerequisites

| Requirement | Why You Need It |
|---|---|
| **Python 3.10+** | Django 6.x requires Python 3.10 or higher |
| **pip** | Python's package installer — comes bundled with Python |
| **A text editor/IDE** | VS Code, PyCharm, or any editor you're comfortable with |
| **Terminal/Command Line** | You'll run all commands from here |
| Basic Python knowledge | Variables, functions, classes, imports |

> [!TIP]
> **New to the terminal?** Every command in this guide starts with `$`. You type everything *after* the `$`. Lines without `$` are output you should expect to see.

---

## Project Structure Overview

Before we start, here's what your project will look like when you're done. Refer back to this map when you feel lost:

```
EduFinApp/                  <- Root project directory
├── manage.py               <- Django's command-line utility (you never edit this)
├── requirements.txt        <- Lists all Python packages your project needs
├── db.sqlite3              <- Your database file (auto-created after migrations)
│
├── EduFinApp/              <- Project configuration folder (same name as root)
│   ├── __init__.py         <- Marks this folder as a Python package
│   ├── settings.py         <- All project settings live here
│   ├── urls.py             <- The "table of contents" for your URLs
│   ├── wsgi.py             <- Entry point for web servers (don't touch)
│   └── asgi.py             <- Async entry point (don't touch)
│
├── accounts/               <- App for user/authentication logic
│   ├── models.py           <- Custom User model
│   ├── admin.py            <- Register models with Django Admin
│   └── ...
│
├── core/                   <- App for main business logic
│   ├── models.py           <- Database models (e.g., Testing)
│   ├── serializers.py      <- Converts models to/from JSON
│   ├── views.py            <- Handles requests and returns responses
│   └── ...
│
└── templates/              <- HTML templates (optional for APIs)
    └── core/
        └── testing.html
```

> [!NOTE]
> **Django Project vs App:**
> - A **project** is the entire web application (EduFinApp).
> - An **app** is a self-contained module that does one thing (e.g., `accounts` handles users, `core` handles business logic).
> - A project can have many apps. Apps can be reused across projects.

---

## Step 1: Project Initialization and Environment Setup

### Learning Objective
Set up an isolated Python environment and install the tools you need.

### Why Virtual Environments?
Imagine you have two projects: one needs Django 4.x, the other needs Django 6.x. Without virtual environments, they'd fight over which version is installed. A **virtual environment** gives each project its own isolated set of packages.

### Instructions

**1.1 — Create a project directory and navigate into it:**
```bash
$ mkdir EduFinApp
$ cd EduFinApp
```

**1.2 — Create and activate a virtual environment:**
```bash
# Create the virtual environment (a folder called .venv will appear)
$ python -m venv .venv

# Activate it
# On macOS/Linux:
$ source .venv/bin/activate

# On Windows:
# $ .venv\Scripts\activate
```

> After activation, your terminal prompt should change — you'll see `(.venv)` at the beginning. This confirms you're inside the virtual environment.

**1.3 — Create `requirements.txt`:**

Create a file called `requirements.txt` in your project root. This file tells `pip` exactly which packages (and versions) to install.

```text
asgiref==3.11.1
Django==6.0.3
django-filter==25.2
djangorestframework==3.16.1
Markdown==3.10.2
sqlparse==0.5.5
```

> [!NOTE]
> **What are these packages?**
> | Package | Purpose |
> |---|---|
> | `Django` | The web framework itself |
> | `djangorestframework` | Adds powerful API-building tools on top of Django |
> | `django-filter` | Lets you filter querysets via URL parameters |
> | `sqlparse` | Formats SQL queries (used internally by Django) |
> | `asgiref` | Handles async support for Django |
> | `Markdown` | Enables Markdown rendering in DRF's browsable API |

**1.4 — Install all dependencies:**
```bash
$ pip install -r requirements.txt
```

You should see output ending with something like:
```
Successfully installed Django-6.0.3 djangorestframework-3.16.1 ...
```

**1.5 — Initialize the Django project:**
```bash
$ django-admin startproject EduFinApp .
```

> [!IMPORTANT]
> **Don't miss the `.` (dot) at the end!** The dot tells Django to create the project *in the current directory* instead of creating a nested folder. Without it, you'd get `EduFinApp/EduFinApp/EduFinApp/` — confusing!

**1.6 — Create two apps:**
```bash
$ python manage.py startapp accounts
$ python manage.py startapp core
```

> **Why two apps?** Separation of concerns. `accounts` will handle everything user-related (login, registration, profiles). `core` will handle the main business logic of the application.

### Checkpoint
At this point, your directory should look like this:
```
EduFinApp/
├── manage.py
├── requirements.txt
├── EduFinApp/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── ...
├── accounts/
│   ├── models.py
│   └── ...
└── core/
    ├── models.py
    └── ...
```

### Challenge 1: Verify Your Setup
Run this command to verify Django is installed correctly:
```bash
$ python -m django --version
```
**Expected output:** `6.0.3`

Then try starting the development server:
```bash
$ python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser. You should see Django's default **"The install worked successfully!"** page. Press `Ctrl+C` to stop the server.

<details>
<summary>Troubleshooting: "Command not found" or "Module not found"</summary>

- **Is your virtual environment active?** Check for `(.venv)` in your terminal prompt.
- **Did `pip install` succeed?** Run `pip list` to see installed packages.
- **Are you in the right directory?** Run `ls` (macOS/Linux) or `dir` (Windows) — you should see `manage.py`.
</details>

---


## Step 2: Custom User Model in `accounts` App

### Learning Objective
Create a custom User model that extends Django's built-in authentication system.

### Why a Custom User Model?

Django comes with a built-in `User` model that has fields like `username`, `email`, and `password`. So why replace it?

> Because **changing the User model mid-project is extremely painful**. If you start with Django's default `User` and later realize you need to add fields like `phone_number` or `role`, you'll face a nightmare of database migrations. Starting with a custom model — even an empty one — future-proofs your project.

### Instructions

**2.1 — Open `accounts/models.py` and replace its contents with:**

```python
from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    pass
```

### Code Breakdown

| Line | What It Does |
|---|---|
| `from django.contrib.auth.models import AbstractUser` | Imports Django's base user class that includes all default fields (username, email, password, etc.) |
| `class User(AbstractUser):` | Creates your custom `User` class that **inherits** everything from `AbstractUser` |
| `pass` | A Python keyword meaning "nothing here yet." The class works exactly like the default User for now, but you can add custom fields later |

> [!TIP]
> **Later, you could extend this model** by adding custom fields like:
> ```python
> class User(AbstractUser):
>     phone_number = models.CharField(max_length=15, blank=True)
>     date_of_birth = models.DateField(null=True, blank=True)
>     role = models.CharField(max_length=20, default='student')
> ```
> Because you started with a custom model, adding these fields is a simple migration — no pain!
### Challenge 2: Extend the User Model

Now that you have a custom User, **put it to work**. Add a `role` field so each user can be labeled as a `student` or `instructor`.

**Your task:**
1. Open `accounts/models.py`
2. Add a `role` field using `models.CharField` with a `max_length` of `20` and a `default` value of `'student'`
3. Save the file

> You won't run migrations yet — we'll do that in Step 8. For now, just make sure the file saves without syntax errors.

<details>
<summary>Hint</summary>

Look at the TIP box above this challenge — it shows how to add fields to a model that inherits from `AbstractUser`. Your `role` field follows the same pattern. Remember that each field is a class-level attribute assigned a `models.<FieldType>(...)`.
</details>

---

## Step 3: Configure Project Settings

### Learning Objective
Register your apps and third-party packages, and tell Django to use your custom User model.

### Why This Matters
Django doesn't automatically know about apps you create — you must **register** them explicitly. Think of `settings.py` as the brain of your project: it controls everything from which database to use, to which apps are active.

### Instructions

**3.1 — Open `EduFinApp/settings.py` and find the `INSTALLED_APPS` list. Update it to:**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # --- Your apps ---
    'core.apps.CoreConfig',
    'accounts',
    # --- Third-party apps ---
    'rest_framework',
]
```

### Code Breakdown

| Entry | What It Is |
|---|---|
| `django.contrib.admin` | Built-in admin interface |
| `django.contrib.auth` | Built-in authentication system |
| `django.contrib.contenttypes` | Tracks all models in the project |
| `django.contrib.sessions` | Manages user sessions |
| `django.contrib.messages` | Flash message framework |
| `django.contrib.staticfiles` | Serves CSS, JS, and image files |
| `core.apps.CoreConfig` | Registers your `core` app (using its config class) |
| `accounts` | Registers your `accounts` app (shorthand style) |
| `rest_framework` | Enables Django REST Framework |

> [!NOTE]
> **Two ways to register an app:**
> - `'accounts'` — shorthand, works fine.
> - `'core.apps.CoreConfig'` — explicit, uses the app's configuration class from `core/apps.py`. Both are valid.

**3.2 — Configure the templates directory. Find the `TEMPLATES` setting and update `DIRS`:**

```python
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]
```

> **What is `BASE_DIR / 'templates'`?** `BASE_DIR` is a `Path` object pointing to your project root. The `/` operator joins paths. So this resolves to something like `/home/you/EduFinApp/templates`.

**3.3 — Tell Django to use your custom User model. Add this line at the very end of `settings.py`:**

```python
AUTH_USER_MODEL = 'accounts.User'
```

> [!CAUTION]
> **This line MUST be added BEFORE you run any migrations.** If you migrate first, Django creates tables for the default User model. Switching to a custom User model after that requires deleting and recreating the database — a headache you want to avoid.

### Challenge 3: Create and Register a New App

Practice the full app-creation cycle by adding a **third app** called `transactions`.

**Your task:**
1. Run the command to create a new app called `transactions`
2. Open `EduFinApp/settings.py` and register it in `INSTALLED_APPS`
3. Verify it worked by checking that the `transactions/` folder was created with its own `models.py`, `views.py`, etc.

<details>
<summary>Hint</summary>

The command to create a new app follows the same pattern you used for `accounts` and `core` in Step 1.6 — it uses `python manage.py startapp <app_name>`. After creating the folder, add the app name as a string to the `INSTALLED_APPS` list in `settings.py`, just like `'accounts'` is listed there.
</details>

---

## Step 4: Create the `Testing` Model in `core` App

### Learning Objective
Define a database model — a Python class that Django automatically converts into a database table.

### How Django Models Work

In Django, you **never write SQL** to create tables. Instead, you define a Python class that inherits from `models.Model`. Django's ORM (Object-Relational Mapper) translates this class into a database table.

```
Python Class (Model) ---- Django ORM ----> Database Table
     Field              ========>              Column
     Instance           ========>              Row
```

### Instructions

**4.1 — Open `core/models.py` and replace its contents with:**

```python
from django.db import models

class Testing(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name
```

### Code Breakdown

| Line | What It Does |
|---|---|
| `class Testing(models.Model):` | Defines a model called `Testing`. Inheriting from `models.Model` tells Django "this is a database table" |
| `name = models.CharField(max_length=200)` | Creates a text column with a **maximum of 200 characters**. Good for titles, names, etc. |
| `description = models.TextField()` | Creates a text column with **no length limit**. Good for long descriptions |
| `def __str__(self):` | A special Python method that controls how the object displays as text |
| `return self.name` | When you print a `Testing` object or see it in Django Admin, it shows the `name` field instead of `Testing object (1)` |

> [!NOTE]
> **Django automatically adds an `id` field** to every model. You don't need to define it — each record gets a unique auto-incrementing integer ID. So your actual table columns will be: `id`, `name`, `description`.

### What the Database Table Looks Like

| id | name | description |
|---|---|---|
| 1 | "Financial Literacy" | "A course on budgeting basics" |
| 2 | "Investment 101" | "Introduction to stocks and bonds" |

### Challenge 4: Model Extension
Add a **third field** to the `Testing` model called `created_at` that automatically records the date and time each record is created.

<details>
<summary>Hint</summary>

Django has a field type called `DateTimeField`. Look up the `auto_now_add` parameter — when set to `True`, it tells Django to automatically stamp the current date and time when a record is first created. Add this field after `description` in your model, following the same `field_name = models.<FieldType>(...)` pattern.
</details>

---

## Step 5: Set Up Django REST Framework Serializers

### Learning Objective
Create a serializer that converts model instances (Python objects) into JSON data (and vice versa).

### What is a Serializer and Why Do You Need One?

APIs communicate using **JSON** (JavaScript Object Notation) — a text format that looks like Python dictionaries. But Django models are **Python objects**, not JSON. You need something to translate between them.

```
Database Record (Python Object)
    |  Serialization
    v
JSON (what your API returns)
    |  Deserialization
    v
Database Record (Python Object)
```

**A Serializer does three critical things:**
1. **Serialization:** Converts a Python model instance to JSON (for API responses)
2. **Deserialization:** Converts JSON to Python data (for processing API requests)
3. **Validation:** Ensures incoming data meets your rules before saving to the database

### Instructions

**5.1 — Create a new file `core/serializers.py`** (this file doesn't exist yet — you must create it):

```python
from rest_framework import serializers
from core.models import Testing

class TestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testing
        fields = '__all__'
```

### Code Breakdown

| Line | What It Does |
|---|---|
| `from rest_framework import serializers` | Imports DRF's serializer toolkit |
| `from core.models import Testing` | Imports the model we want to serialize |
| `class TestingSerializer(serializers.ModelSerializer):` | Creates a serializer that's **automatically generated** from the model. `ModelSerializer` reads your model's fields and creates matching serializer fields |
| `class Meta:` | An inner class that configures the serializer |
| `model = Testing` | Tells the serializer which model to work with |
| `fields = '__all__'` | Include **all** fields from the model (`id`, `name`, `description`) |

> [!TIP]
> **`fields = '__all__'` vs explicit fields:**
> Using `'__all__'` is quick for development, but in production you should list fields explicitly for security:
> ```python
> fields = ['id', 'name', 'description']
> ```
> This prevents accidentally exposing sensitive fields you might add later.

### How Serialization Works in Practice

```python
# Imagine you have this record in your database:
# Testing(id=1, name="Financial Literacy", description="Budgeting basics")

# The serializer converts it to:
{
    "id": 1,
    "name": "Financial Literacy",
    "description": "Budgeting basics"
}
```

### Challenge 5: Build a Second Serializer with Explicit Fields

In the main guide you used `fields = '__all__'`. Now practice the **production-ready** approach: listing fields explicitly. You'll also create a brand-new serializer for a different use case.

**Your task:**
1. In `core/serializers.py`, create a **second** serializer class called `TestingNameSerializer`
2. It should also point to the `Testing` model
3. But it should **only** expose the `id` and `name` fields — not `description`

> This is a common pattern: different serializers for different API endpoints (e.g., a list view shows fewer fields than a detail view).

<details>
<summary>Hint</summary>

Your new class will follow the exact same structure as `TestingSerializer` — it inherits from `serializers.ModelSerializer` and has an inner `class Meta`. The only difference is the `fields` attribute: instead of `'__all__'`, set it to a Python list containing only the field names you want to include.
</details>

---

## Step 6: Implement Views and URLs

### Learning Objective
Create a view function that handles HTTP requests and wire it to a URL.

### How the Request-Response Cycle Works

When someone visits `http://127.0.0.1:8000/testing`, here's what happens:

```
Browser Request (GET /testing)
        |
    urls.py    --> "Does /testing match any URL pattern?"
        |          --> Yes! Route to testing_view
    views.py   --> testing_view() runs
        |
    Response   --> JSON sent back to the browser
```

### Instructions

**6.1 — Open `core/views.py` and replace its contents with:**

```python
from django.http import JsonResponse
from django.shortcuts import render
from core.models import Testing

def testing_view(request):
    # For now, return a simple static JSON response
    return JsonResponse({'message': 'Hello, world!'})
```

### Code Breakdown

| Line | What It Does |
|---|---|
| `from django.http import JsonResponse` | Imports a class that returns JSON-formatted HTTP responses |
| `from core.models import Testing` | Imports our model (we'll use it in the capstone challenge) |
| `def testing_view(request):` | Defines a **view function**. Every view receives a `request` object as its first argument — it contains info about the incoming HTTP request (method, headers, body, etc.) |
| `return JsonResponse({...})` | Returns a JSON response. `JsonResponse` automatically sets the `Content-Type` header to `application/json` |

> [!NOTE]
> **Why `JsonResponse` and not `HttpResponse`?**
> - `HttpResponse` returns raw text — you'd have to manually convert your data to JSON and set headers.
> - `JsonResponse` handles both automatically. Always prefer `JsonResponse` for APIs.

**6.2 — Open `EduFinApp/urls.py` and replace its contents with:**

```python
from django.contrib import admin
from django.urls import path
from core.views import testing_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('testing', testing_view, name='testing'),
]
```

### Code Breakdown

| Line | What It Does |
|---|---|
| `from core.views import testing_view` | Imports the view function we just wrote |
| `path('admin/', admin.site.urls)` | Maps `/admin/` to Django's built-in admin interface |
| `path('testing', testing_view, name='testing')` | Maps the URL `/testing` to our `testing_view` function. The `name='testing'` gives this URL a label so you can reference it elsewhere in your code |

> [!TIP]
> **The `name` parameter** allows you to reference this URL by name instead of hard-coding the path. For example, in templates you'd write `{% url 'testing' %}` instead of `/testing`. This way, if you change the URL path later, all references update automatically.

### Challenge 6: Add a Second Endpoint

Practice the full view-to-URL wiring by creating a **health-check** endpoint.

**Your task:**
1. In `core/views.py`, add a **new** function called `health_check` that returns `{"status": "ok"}` as a `JsonResponse`
2. In `EduFinApp/urls.py`, import your new view and wire it to the URL path `health`
3. Start the server, then visit `http://127.0.0.1:8000/health` to confirm it works

<details>
<summary>Hint</summary>

Your new view function follows the exact same pattern as `testing_view` — it takes `request` as a parameter and returns a `JsonResponse` with a dictionary. For the URL, add a new `path(...)` entry to `urlpatterns` and make sure to import your new function at the top of `urls.py` alongside `testing_view`.
</details>

---

## Step 7: Create Templates Directory (Optional)

### Learning Objective
Understand the templates directory structure, even though we're building an API (not a traditional web page).

### Instructions

**7.1 — Create the templates directory and an empty template file:**

```bash
$ mkdir -p templates/core
$ touch templates/core/testing.html
```

> **Why create this if we're not using it?** In a real project, you might want to render HTML pages alongside your API. Django's `render()` function looks for templates in this directory. For now, this is a placeholder for future use.

---

## Step 8: Migrations and Verification

### Learning Objective
Translate your Python models into actual database tables and verify everything works.

### What Are Migrations?

Migrations are Django's way of **syncing your models with the database**. Think of it as a two-step process:

```
Step 1: makemigrations --> "Reads your models, writes a migration file (the blueprint)"
Step 2: migrate         --> "Executes the blueprint, creating/updating tables in the database"
```

### Instructions

**8.1 — Generate migration files:**

```bash
# Create migrations for the accounts app (custom User model)
$ python manage.py makemigrations accounts

# Expected output:
# Migrations for 'accounts':
#   accounts/migrations/0001_initial.py
#     - Create model User

# Create migrations for the core app (Testing model)
$ python manage.py makemigrations core

# Expected output:
# Migrations for 'core':
#   core/migrations/0001_initial.py
#     - Create model Testing
```

**8.2 — Apply the migrations to the database:**
```bash
$ python manage.py migrate
```

You should see output like:
```
Operations to perform:
  Apply all migrations: accounts, admin, auth, contenttypes, core, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying accounts.0001_initial... OK
  ...
  Applying core.0001_initial... OK
```

> [!IMPORTANT]
> **Always run migrations for `accounts` FIRST.** Since you defined a custom User model, Django needs to know about it before processing other apps that may reference the User.

**8.3 — Create a superuser (admin account):**
```bash
$ python manage.py createsuperuser
```

Follow the prompts to set a username, email, and password. You'll use this to log into Django Admin.

**8.4 — Start the development server:**
```bash
$ python manage.py runserver
```

**8.5 — Test your endpoints:**

| URL | Expected Result |
|---|---|
| `http://127.0.0.1:8000/testing` | `{"message": "Hello, world!"}` |
| `http://127.0.0.1:8000/admin/` | Django Admin login page |

### Challenge 7: Admin Registration

Register the `Testing` model in Django Admin so you can add records from the browser.

**Your task:**
1. Open `core/admin.py`
2. Import the `Testing` model
3. Register it with the admin site
4. Visit `http://127.0.0.1:8000/admin/`, log in with your superuser account, and add 2-3 `Testing` records (give them names and descriptions)

<details>
<summary>Hint</summary>

Django's admin registration requires two things: importing your model with `from core.models import Testing`, then calling `admin.site.register(Testing)`. After saving, refresh the admin page — you should see "Testing" listed under the CORE section. These records will be used in the capstone challenge.
</details>

---

## Step 9: Capstone Challenge — Connect Serializers to Views

Now that you have the full stack in place — models, serializers, views, URLs, and data in the database — it's time to bring it all together.

### Part A: Make the Endpoint Dynamic

**Goal:** Modify `core/views.py` so that the `/testing` endpoint returns **real data from the database** instead of a static `"Hello, world!"` message.

You need to:
1. **Query** all `Testing` records from the database
2. **Serialize** them into JSON using `TestingSerializer`
3. **Return** the serialized data as a `JsonResponse`

<details>
<summary>Hint 1: Querying the database</summary>

Django's ORM lets you retrieve all records from a model using `<Model>.objects.all()`. This returns a **QuerySet** — a list-like collection of model instances.
</details>

<details>
<summary>Hint 2: Using the serializer</summary>

To serialize a queryset (multiple objects), you need to tell the serializer that you're passing more than one item. There's a keyword argument for this — check the DRF documentation for `ModelSerializer` or think about what boolean flag signals "there are many items here."
</details>

<details>
<summary>Hint 3: Returning a list in JsonResponse</summary>

By default, `JsonResponse` only accepts **dictionaries** (for security reasons). If your serialized data is a list, you'll need to pass an extra keyword argument to `JsonResponse` to allow non-dict objects. Look up the `safe` parameter.
</details>

**Verify:** Make sure you've added records via Django Admin (Challenge 7), then visit `http://127.0.0.1:8000/testing`. Instead of the static message, you should see a JSON list containing the `id`, `name`, and `description` of each record you added:

```json
[
    {
        "id": 1,
        "name": "Financial Literacy",
        "description": "A course on budgeting basics"
    },
    {
        "id": 2,
        "name": "Investment 101",
        "description": "Introduction to stocks and bonds"
    }
]
```

---

### Part B: Add a Single-Record Detail Endpoint

Now go further. Create a **second endpoint** that returns a **single** `Testing` record by its `id`.

**Your task:**
1. In `core/views.py`, create a new view function called `testing_detail_view` that:
   - Accepts an `id` parameter from the URL
   - Retrieves a single `Testing` object matching that `id`
   - Serializes it using `TestingSerializer` (this time for a single object, not a list)
   - Returns the serialized data as a `JsonResponse`
2. In `EduFinApp/urls.py`, add a URL pattern that captures an integer `id` from the URL and passes it to your new view

**Expected behavior:**
- Visiting `http://127.0.0.1:8000/testing/1` should return only the record with `id=1`
- Visiting `http://127.0.0.1:8000/testing/2` should return only the record with `id=2`

<details>
<summary>Hint 1: Capturing a URL parameter</summary>

Django's `path()` function supports **path converters** to capture parts of the URL. The syntax `<int:id>` captures an integer from the URL and passes it as a keyword argument to the view function. For example: `path('testing/<int:id>', my_view, name='...')`.
</details>

<details>
<summary>Hint 2: Getting a single object from the database</summary>

Instead of `.objects.all()`, you can retrieve a single record with `.objects.get(id=id)`. However, if no record exists with that ID, Django will raise a `DoesNotExist` exception. Think about how you might handle that — consider looking up `get_object_or_404` from `django.shortcuts`.
</details>

<details>
<summary>Hint 3: Serializing a single object</summary>

When you serialize a single object (not a queryset), you do NOT pass the `many=True` argument. The serializer expects a single model instance, and `.data` will return a dictionary instead of a list — which means you won't need the `safe=False` workaround in `JsonResponse` either.
</details>

---

### Part C: Handle "Not Found" Gracefully

What happens when a user visits `/testing/999` and no record with `id=999` exists? Right now, your app would crash with an error.

**Your task:**
1. Modify `testing_detail_view` so that if the requested `id` doesn't exist, the API returns a **proper error response** instead of crashing
2. The error response should be a `JsonResponse` with an appropriate error message and an HTTP status code of `404`

<details>
<summary>Hint</summary>

You can use a `try/except` block to catch the `Testing.DoesNotExist` exception. In the `except` block, return a `JsonResponse` with an error message. `JsonResponse` accepts a `status` keyword argument — set it to `404` to indicate "not found."
</details>

**Verify:**
- `http://127.0.0.1:8000/testing/1` returns the record (status 200)
- `http://127.0.0.1:8000/testing/999` returns an error message like `{"error": "Record not found"}` (status 404)

> **Congratulations!** You've built a working API that reads data from a database, serializes it, returns it as JSON, handles both list and detail views, and gracefully handles errors. This is the foundation of every Django REST API!

---

## Quick Reference: Key Concepts

| Concept | What It Does | File |
|---|---|---|
| **Model** | Defines database table structure | `models.py` |
| **Migration** | Syncs model changes to the database | `migrations/` |
| **Serializer** | Converts Python objects to/from JSON | `serializers.py` |
| **View** | Handles requests, returns responses | `views.py` |
| **URL Pattern** | Maps URLs to views | `urls.py` |
| **Admin** | Web interface for managing data | `admin.py` |

---

## Useful Resources

- [Django Documentation](https://docs.djangoproject.com/en/6.0/) — The official Django docs
- [Django REST Framework Documentation](https://www.django-rest-framework.org/) — DRF's official guide
- [Django REST Framework Tutorial](https://www.django-rest-framework.org/tutorial/quickstart/) — A hands-on quickstart
- [Python Classes & Inheritance](https://docs.python.org/3/tutorial/classes.html) — If you need to review OOP concepts
