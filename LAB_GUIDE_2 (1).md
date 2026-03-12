# Lab 2: Building a Full CRUD API with Django REST Framework

## What You Will Build

In this lab, you will transform EduFinApp from a simple read-only endpoint into a **fully functional CRUD API**. By the end, your API will be able to **Create**, **Read**, **Update**, and **Delete** records — the four fundamental operations of any data-driven application.

You will learn:
- How to use DRF's `APIView` class instead of plain Django function views
- How to handle different HTTP methods (GET, POST, PUT, DELETE) in a single view
- How to organize URLs using app-level routing with `include()`
- How to validate incoming data using serializers
- How to build a real financial model (`Transaction`) and expose it via the API

> **Who is this for?** Students who have completed Lab 1. You should have a working EduFinApp project with the `Testing` model, serializer, and a basic view returning JSON.

---

## Prerequisites

| Requirement | Why You Need It |
|---|---|
| **Completed Lab 1** | This lab builds directly on the project you created |
| **Lab 1 server runs successfully** | Run `python manage.py runserver` and confirm `/testing` returns data |
| **Postman, curl, or httpie** | You'll need a tool to send POST, PUT, and DELETE requests (browsers only send GET) |

> [!TIP]
> **Don't have Postman?** You can use `curl` from the terminal. We'll provide `curl` examples throughout this guide. Alternatively, DRF's built-in **Browsable API** (which you'll enable in this lab) provides a web interface for testing.

---

## Concepts You Need to Know

Before we start coding, let's understand the building blocks.

### What is CRUD?

CRUD maps directly to HTTP methods — this is the language every REST API speaks:

| Operation | HTTP Method | What It Does | Example |
|---|---|---|---|
| **Create** | POST | Add a new record | Add a new transaction |
| **Read** | GET | Retrieve record(s) | View all transactions |
| **Update** | PUT | Modify an existing record | Change a transaction amount |
| **Delete** | DELETE | Remove a record | Delete a transaction |

### Function Views vs Class-Based Views

In Lab 1, you wrote **function views** — simple Python functions that handle requests. They work, but they get messy fast when you need to handle multiple HTTP methods:

```python
# Function view approach — gets messy with multiple methods
def my_view(request):
    if request.method == 'GET':
        # handle read
    elif request.method == 'POST':
        # handle create
    elif request.method == 'PUT':
        # handle update
    elif request.method == 'DELETE':
        # handle delete
```

DRF's `APIView` solves this by giving each HTTP method its own clean function:

```python
# Class-based view approach — clean and organized
class MyView(APIView):
    def get(self, request):       # handles GET
        ...
    def post(self, request):      # handles POST
        ...
    def put(self, request, id):   # handles PUT
        ...
    def delete(self, request, id): # handles DELETE
        ...
```

### What is `APIView`?

`APIView` is DRF's base class for building API views. Compared to Django's plain views, it adds:
- **Automatic request parsing** — JSON request bodies are parsed for you
- **DRF Response objects** — richer than `JsonResponse`, with status codes and content negotiation
- **Built-in error handling** — malformed requests return proper error responses
- **Browsable API** — a web UI for testing your endpoints (no Postman needed for basic testing)

---

## Step 1: Create the Transaction Model

The `Testing` model from Lab 1 was a placeholder. Now let's build something real — a `Transaction` model that tracks financial transactions.

### Learning Objective
Design a model with relationships (ForeignKey) and different field types.

### Instructions

**1.1 — Open `core/models.py` and add the `Transaction` model below the existing `Testing` model:**

```python
from django.db import models
from django.conf import settings

class Testing(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()

    def __str__(self):
        return self.name


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('income', 'Income'),
        ('expense', 'Expense'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    title = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_type = models.CharField(
        max_length=7,
        choices=TRANSACTION_TYPES,
        default='expense'
    )
    category = models.CharField(max_length=100, blank=True)
    date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} - {self.amount}"
```

### Code Breakdown

| Element | What It Does |
|---|---|
| `TRANSACTION_TYPES` | A list of valid choices. Django enforces these in forms and admin — only `'income'` or `'expense'` are allowed |
| `ForeignKey(settings.AUTH_USER_MODEL, ...)` | Creates a **relationship** — each transaction belongs to one user. `settings.AUTH_USER_MODEL` references your custom User model |
| `on_delete=models.CASCADE` | If a user is deleted, all their transactions are deleted too |
| `related_name='transactions'` | Lets you access a user's transactions with `user.transactions.all()` |
| `DecimalField(max_digits=10, decimal_places=2)` | Stores monetary values precisely (up to 99,999,999.99). Never use `FloatField` for money — it causes rounding errors |
| `choices=TRANSACTION_TYPES` | Restricts valid values for this field |
| `blank=True` | The field is optional in forms (the user doesn't have to fill it in) |
| `auto_now_add=True` | Automatically stamps the current time when a record is created |

**1.2 — Run migrations:**

```bash
$ python manage.py makemigrations core
$ python manage.py migrate
```

**1.3 — Register the model in admin. Open `core/admin.py`:**

```python
from django.contrib import admin
from core.models import Testing, Transaction

admin.site.register(Testing)
admin.site.register(Transaction)
```

### Challenge 1: Add a Second Model

Create a `Budget` model in `core/models.py` that has the following fields:
- `user` — a ForeignKey to the User model (same pattern as Transaction)
- `name` — a CharField with max_length of 100 (e.g., "Monthly Groceries")
- `limit_amount` — a DecimalField for the budget cap
- `month` — a DateField representing which month this budget is for

Then run migrations and register it in admin.

<details>
<summary>Hint</summary>

Follow the exact same pattern as `Transaction`. Each field uses `models.<FieldType>(...)`. For the ForeignKey, use `settings.AUTH_USER_MODEL` as the first argument. Don't forget to import `settings` from `django.conf` if it's not already imported. After defining the model, run `makemigrations` and `migrate`, then add `admin.site.register(Budget)` in `core/admin.py`.
</details>

---

## Step 2: Create the Transaction Serializer

### Learning Objective
Build a serializer with validation rules that reject bad data before it reaches the database.

### Instructions

**2.1 — Open `core/serializers.py` and add the `TransactionSerializer`:**

```python
from rest_framework import serializers
from core.models import Testing, Transaction

class TestingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testing
        fields = '__all__'


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'title', 'amount', 'transaction_type', 'category', 'date', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']

    def validate_amount(self, value):
        """Ensure the amount is a positive number."""
        if value <= 0:
            raise serializers.ValidationError("Amount must be greater than zero.")
        return value

    def validate_title(self, value):
        """Ensure the title is not empty or just whitespace."""
        if not value.strip():
            raise serializers.ValidationError("Title cannot be blank.")
        return value
```

### Code Breakdown

| Element | What It Does |
|---|---|
| `fields = ['id', 'user', ...]` | Explicitly lists which fields to include — the production-ready approach instead of `'__all__'` |
| `read_only_fields` | These fields are returned in responses but **ignored** in incoming requests. The `user` is set by the server (not the client), `id` and `created_at` are auto-generated |
| `validate_amount(self, value)` | A **field-level validator** — DRF automatically calls `validate_<fieldname>` for each field. If validation fails, it raises `ValidationError` and DRF returns a 400 response |
| `validate_title(self, value)` | Another field-level validator — ensures titles aren't empty whitespace |

> [!NOTE]
> **How DRF validation works:** When data comes in via a POST or PUT request, the serializer's `is_valid()` method runs all validators. If any fail, `serializer.errors` contains the error details and nothing is saved to the database. This is your first line of defense for data integrity.

### Challenge 2: Add Cross-Field Validation

Add a `validate` method (not `validate_<field>` — just `validate`) to `TransactionSerializer` that checks: if `transaction_type` is `'income'`, the `category` field must not be empty.

<details>
<summary>Hint</summary>

A method called `validate(self, data)` receives the entire dictionary of validated fields as `data`. You can access individual fields with `data.get('field_name')` or `data['field_name']`. If the check fails, raise `serializers.ValidationError({"category": "Category is required for income transactions."})`. Return `data` at the end if everything passes.
</details>

---

## Step 3: Build CRUD Views with APIView

### Learning Objective
Use DRF's `APIView` to handle GET, POST, PUT, and DELETE requests in organized class-based views.

### Instructions

You'll create two views:
- `TransactionListView` — handles listing all transactions (GET) and creating new ones (POST)
- `TransactionDetailView` — handles retrieving (GET), updating (PUT), and deleting (DELETE) a single transaction

**3.1 — Open `core/views.py` and replace its contents with:**

```python
from django.http import JsonResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.models import Testing, Transaction
from core.serializers import TestingSerializer, TransactionSerializer


# --- Existing views from Lab 1 ---

def testing_view(request):
    data = Testing.objects.all()
    serializer = TestingSerializer(data, many=True)
    return JsonResponse(serializer.data, safe=False)


# --- New CRUD views ---

class TransactionListView(APIView):
    """
    GET  /api/transactions/     -> List all transactions
    POST /api/transactions/     -> Create a new transaction
    """

    def get(self, request):
        transactions = Transaction.objects.all()
        serializer = TransactionSerializer(transactions, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = TransactionSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TransactionDetailView(APIView):
    """
    GET    /api/transactions/<id>/  -> Retrieve a single transaction
    PUT    /api/transactions/<id>/  -> Update a transaction
    DELETE /api/transactions/<id>/  -> Delete a transaction
    """

    def get_object(self, id):
        try:
            return Transaction.objects.get(id=id)
        except Transaction.DoesNotExist:
            return None

    def get(self, request, id):
        transaction = self.get_object(id)
        if transaction is None:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TransactionSerializer(transaction)
        return Response(serializer.data)

    def put(self, request, id):
        transaction = self.get_object(id)
        if transaction is None:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = TransactionSerializer(transaction, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, id):
        transaction = self.get_object(id)
        if transaction is None:
            return Response(
                {"error": "Transaction not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        transaction.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
```

### Code Breakdown

**TransactionListView:**

| Element | What It Does |
|---|---|
| `class TransactionListView(APIView):` | A class-based view where each method name matches an HTTP verb |
| `def get(self, request):` | Runs when a GET request hits this endpoint |
| `Response(serializer.data)` | DRF's `Response` — smarter than `JsonResponse`. It handles content negotiation and powers the browsable API |
| `data=request.data` | In the `post` method, `request.data` contains the parsed JSON body sent by the client |
| `serializer.is_valid()` | Runs all validation rules. Returns `True` if data is clean, `False` if not |
| `serializer.save(user=request.user)` | Saves to the database. `user=request.user` sets the `user` field to whoever made the request (since it's a `read_only_field`, it's not in the request body) |
| `status.HTTP_201_CREATED` | Returns HTTP 201 — the standard status code for "resource created successfully" |

**TransactionDetailView:**

| Element | What It Does |
|---|---|
| `def get_object(self, id):` | A helper method that retrieves a single transaction or returns `None` if not found — avoids repeating this logic in every method |
| `TransactionSerializer(transaction, data=request.data)` | In the `put` method, passing both the existing instance and new data tells the serializer to **update** the instance instead of creating a new one |
| `transaction.delete()` | Removes the record from the database |
| `HTTP_204_NO_CONTENT` | Standard response for successful deletion — "it worked, but there's no content to return" |

---

## Step 4: App-Level URL Routing

### Learning Objective
Organize URLs by creating a separate `urls.py` inside each app and connecting them to the main project URLs using `include()`.

### Why App-Level URLs?

In Lab 1, all URLs lived in `EduFinApp/urls.py`. As your project grows, this file becomes a nightmare. Instead, each app should manage its own URLs, and the project `urls.py` connects them together.

```
EduFinApp/urls.py (project level)
    |
    |--> "api/" --> core/urls.py (app level)
    |                 |--> "transactions/"     -> TransactionListView
    |                 |--> "transactions/<id>/" -> TransactionDetailView
    |
    |--> "admin/" --> Django Admin
```

### Instructions

**4.1 — Create a new file `core/urls.py`:**

```python
from django.urls import path
from core.views import testing_view, TransactionListView, TransactionDetailView

urlpatterns = [
    path('testing/', testing_view, name='testing'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
    path('transactions/<int:id>/', TransactionDetailView.as_view(), name='transaction-detail'),
]
```

### Code Breakdown

| Element | What It Does |
|---|---|
| `.as_view()` | Class-based views must be converted to a function with `.as_view()` before being passed to `path()` — this is how Django knows how to call them |
| `<int:id>` | A path converter that captures an integer from the URL and passes it as the `id` argument to the view |

**4.2 — Update the project-level `EduFinApp/urls.py` to use `include()`:**

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
]
```

### Code Breakdown

| Element | What It Does |
|---|---|
| `include('core.urls')` | Tells Django: "for any URL starting with `api/`, hand it off to `core/urls.py` to figure out the rest" |
| The `api/` prefix | All core app endpoints now live under `/api/`. So the transaction list is at `/api/transactions/` |

> [!NOTE]
> **Your existing `/testing` endpoint has moved.** It's now at `/api/testing/` because of the `api/` prefix. This is a deliberate improvement — all API endpoints live under a common namespace.

### Challenge 3: Create URLs for the Budget Model

If you completed Challenge 1 (the `Budget` model), now wire it up:
1. Create a `BudgetListView` in `core/views.py` that handles GET (list all) and POST (create new)
2. Add URL patterns for it in `core/urls.py`

<details>
<summary>Hint</summary>

Your `BudgetListView` follows the exact same pattern as `TransactionListView` — it inherits from `APIView`, has `get` and `post` methods, uses a serializer, and returns `Response` objects. You'll also need a `BudgetSerializer` in `core/serializers.py` first. In `core/urls.py`, add a new `path('budgets/', BudgetListView.as_view(), name='budget-list')`.
</details>

---

## Step 5: Test the CRUD API

### Learning Objective
Verify that all four CRUD operations work correctly using `curl` or the DRF Browsable API.

### Instructions

**5.1 — Start the server:**
```bash
$ python manage.py runserver
```

**5.2 — Test each operation:**

> [!IMPORTANT]
> The POST, PUT, and DELETE requests below require authentication. For now, we'll temporarily allow unauthenticated access so you can test the CRUD operations. In Lab 3, you'll lock this down properly. If you get `403 Forbidden` errors, add this to `EduFinApp/settings.py`:
> ```python
> REST_FRAMEWORK = {
>     'DEFAULT_PERMISSION_CLASSES': [
>         'rest_framework.permissions.AllowAny',
>     ]
> }
> ```
> **IMPORTANT:** This is for testing only. You will remove this in Lab 3.

**Create a transaction (POST):**
```bash
$ curl -X POST http://127.0.0.1:8000/api/transactions/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Grocery Shopping", "amount": "45.99", "transaction_type": "expense", "category": "Food", "date": "2026-03-11"}'
```

Expected response (status 201):
```json
{
    "id": 1,
    "user": 1,
    "title": "Grocery Shopping",
    "amount": "45.99",
    "transaction_type": "expense",
    "category": "Food",
    "date": "2026-03-11",
    "created_at": "2026-03-11T12:00:00Z"
}
```

**List all transactions (GET):**
```bash
$ curl http://127.0.0.1:8000/api/transactions/
```

**Get a single transaction (GET):**
```bash
$ curl http://127.0.0.1:8000/api/transactions/1/
```

**Update a transaction (PUT):**
```bash
$ curl -X PUT http://127.0.0.1:8000/api/transactions/1/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Weekly Groceries", "amount": "52.00", "transaction_type": "expense", "category": "Food", "date": "2026-03-11"}'
```

**Delete a transaction (DELETE):**
```bash
$ curl -X DELETE http://127.0.0.1:8000/api/transactions/1/
```
Expected: empty response with status 204.

**Test validation — send a negative amount (POST):**
```bash
$ curl -X POST http://127.0.0.1:8000/api/transactions/ \
  -H "Content-Type: application/json" \
  -d '{"title": "Bad Transaction", "amount": "-10.00", "transaction_type": "expense", "date": "2026-03-11"}'
```

Expected response (status 400):
```json
{
    "amount": ["Amount must be greater than zero."]
}
```

### Challenge 4: Test Edge Cases

Test the following scenarios and observe the responses:
1. Send a POST request with a missing required field (omit `title`)
2. Send a PUT request to a transaction ID that doesn't exist (e.g., `/api/transactions/999/`)
3. Send a POST request with `transaction_type` set to `"loan"` (not in the choices list)

<details>
<summary>Hint</summary>

Use `curl` with the same POST/PUT patterns shown above, but modify the JSON body. For the missing field test, simply remove the `"title"` key from the JSON. For the invalid choice test, set `"transaction_type": "loan"`. Observe the error messages DRF returns — it automatically generates helpful validation errors for `choices` fields and required fields.
</details>

---

## Step 6: Browsable API

### Learning Objective
Enable DRF's built-in web interface for testing your API without needing external tools.

### Instructions

The Browsable API is already enabled by default when `rest_framework` is in `INSTALLED_APPS`. You just need to use DRF's `Response` (which you're already doing).

**6.1 — Visit your API in a browser:**

Open `http://127.0.0.1:8000/api/transactions/` in your browser. Instead of raw JSON, you'll see a styled web page with:
- The response data formatted nicely
- A form at the bottom for submitting POST requests
- Navigation links

> This works because DRF's `Response` object performs **content negotiation** — when a browser sends a request (accepting HTML), DRF renders the browsable interface. When `curl` or a frontend app sends a request (accepting JSON), DRF returns raw JSON.

---

## Capstone Challenge: Build a Complete Category API

Build a full CRUD API for a new `Category` model from scratch:

### Part A: The Model

Create a `Category` model in `core/models.py` with:
- `name` — CharField with max_length 100 (required, unique)
- `description` — TextField (optional)
- `created_at` — DateTimeField (auto-set on creation)

Run migrations after creating the model.

<details>
<summary>Hint</summary>

For a unique field, pass `unique=True` to `CharField`. For an optional `TextField`, use `blank=True`. Follow the same migration workflow: `makemigrations core`, then `migrate`.
</details>

### Part B: The Serializer

Create a `CategorySerializer` in `core/serializers.py` with:
- Explicit field listing (not `'__all__'`)
- `id` and `created_at` as read-only
- A validator that prevents duplicate category names (case-insensitive — "Food" and "food" should be considered the same)

<details>
<summary>Hint</summary>

For the case-insensitive uniqueness check, write a `validate_name` method that queries the database: `Category.objects.filter(name__iexact=value)`. If any results exist (and it's not the current instance being updated), raise a `ValidationError`. The `__iexact` lookup performs a case-insensitive exact match.
</details>

### Part C: Views and URLs

Create `CategoryListView` and `CategoryDetailView` following the same pattern as the Transaction views. Wire them to `/api/categories/` and `/api/categories/<id>/`.

<details>
<summary>Hint</summary>

Copy the structure of `TransactionListView` and `TransactionDetailView`. The key differences: `Category` doesn't need a `user` field, so you can remove the `user=request.user` from `serializer.save()`. Don't forget to import your new model and serializer, and add the URL patterns in `core/urls.py`.
</details>

### Part D: Verify

Test all operations: create 3 categories, list them, update one, delete one, and try creating a duplicate name to verify your validation catches it.

> **Congratulations!** You now have a full CRUD API with validation, proper URL routing, and DRF's class-based views. In Lab 3, you'll learn how to secure it all.

---

## Quick Reference: Key Concepts from This Lab

| Concept | What It Does |
|---|---|
| **APIView** | DRF's base class for organized, method-based request handling |
| **Response** | DRF's response class — supports content negotiation and the browsable API |
| **status codes** | `201 Created`, `204 No Content`, `400 Bad Request`, `404 Not Found` |
| **Field validators** | `validate_<field>()` methods on serializers for per-field checks |
| **read_only_fields** | Fields returned in responses but ignored in incoming requests |
| **include()** | Connects app-level URL files to the project-level URL configuration |
| **as_view()** | Converts a class-based view into a callable for URL routing |
| **ForeignKey** | Creates a database relationship between two models |
