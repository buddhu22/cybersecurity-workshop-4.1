# Flask Lost-and-Found Notice Board

**Exercise 4.1 — Secure Application Development workshop**

## Problem statement

A simple notice board can help users record synthetic lost and found item notices and mark them resolved. This project demonstrates a small local Flask application with server-side validation and JSON persistence.

## Features

- Browse notice cards and view individual details.
- Create Lost or Found notices.
- Mark notices Resolved using POST.
- Filter notices by category and location zone.
- Store records in a local JSON file.
- Show custom 404 and 500 pages, with technical details kept in local logs.

## Technology stack

Python 3.10+, Flask, JSON, pathlib, datetime, logging, Jinja templates, and CSS. `requirements.txt` contains only Flask.

## Project structure

```text
exercise_4_1/
├── app.py
├── database.py
├── requirements.txt
├── README.md
├── .gitignore
├── data/notices.json
├── templates/ (base, index, detail, create, error, 404)
├── static/style.css
├── logs/app.log
├── tests/test_cases.md
└── docs/ (architecture.md, security_notes.md)
```

## Data model

Each notice stores `id`, `item_type`, `item_category`, `description`, `location_zone`, `date_lost_found`, `contact_preference`, `status`, and ISO-style `created_at`. IDs use sequential `N001` format and skip IDs already in use. The sample JSON contains four synthetic notices.

## Flask routes

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | List notices and optionally filter using `category` and `location` query parameters. |
| GET | `/notice/<id>` | View notice details. |
| GET | `/create` | Show the create form. |
| POST | `/create` | Validate and save a notice, then redirect to its details (Post/Redirect/Get). |
| POST | `/notice/<id>/resolve` | Mark a notice resolved and redirect to its details. |

## Validation rules

The server accepts only Lost/Found types, listed categories, listed location zones, and listed contact preferences. Description is required and limited to 500 characters. The date must be a real ISO date and cannot be in the future. Invalid submissions return the form with a clear field error.

## Security practices

- State changes use POST and successful create uses Post/Redirect/Get.
- Input is validated server-side against allowed values and a description length limit.
- Jinja autoescaping displays descriptions as text; no `safe` filter or unsafe HTML rendering is used.
- JSON errors are handled without exposing tracebacks; technical details go to `logs/app.log`.
- Sample data is synthetic; the form does not request real contact details.
- The app binds to `127.0.0.1` with debug mode off and uses pathlib based on the project location.

See [docs/security_notes.md](docs/security_notes.md) and [docs/architecture.md](docs/architecture.md).

## Installation and run

From the project directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000). The development server should remain local during the workshop. Alternatively, run `flask --app app run --host 127.0.0.1`.

## Testing

See [tests/test_cases.md](tests/test_cases.md) for 12 manual cases, including invalid input, filtering, resolution, malformed JSON, XSS-looking input, unknown routes, and browser refresh after submission. The app can also be exercised with Flask's built-in test client.

## Extension feature

The home page filters by both item category and location using GET query parameters. Filtering only affects the displayed list; it does not modify stored notices.

## Limitations and synthetic data disclaimer

This is a local educational prototype. It has no authentication, CSRF protection, concurrency controls, or production deployment configuration. JSON is suitable for this small exercise only. Do not add real campus information, personally identifying details, or real contact information.
