# CityTrip

## Project Idea

CityTrip is a web application for people who plan spontaneous city trips.
Local restaurant owners, bar owners, and event organizers can add their locations or events to the platform.

Users can then see available activities in a city and discover new places easily.

## Goal

The goal of the project is to create a clear and simple platform that:

* Shows local events and restaurants
* Gives small businesses more visibility
* Helps users quickly find activities in a city

## Technologies

The project is planned as a web application with:

* Frontend (GUI)
* Backend (API)
* Database for storing locations and events
=======
# CityTrip Backend

This backend provides a small FastAPI-based API for CityTrip.

## Quick setup

- Create virtualenv and install dependencies from `requirements.txt`.
- Run the app (from `cityTrip` dir):

```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Database: a local SQLite file `citytrip.db` is used by default. On startup, tables are created automatically.

## Auth

Base paths: `/auth`

- `POST /auth/register`  
  Request JSON: `{ "name": "..", "email": "..", "password": ".." }`  
  Response: user object `{ id, name, email, rolle }`  
  Notes: registers a new user (email must be unique).

- `POST /auth/login`  
  Form-encoded body expected (OAuth2 password grant): `username=<email>&password=<pw>`  
  Response: `{ "access_token": "...", "token_type": "bearer" }`  
  Notes: use the returned bearer token in `Authorization: Bearer <token>` for protected endpoints.

## User (personal) endpoints

Base path: `/me` (requires `Authorization: Bearer <token>`)

- `GET /me/profile`  
  Returns a JSON with your `name`, `favorites` (list of activities you've favourited) and `my_activities` (activities you created). Example:
  ```json
  {
    "name": "Test User",
    "favorites": [{ "id": 1, "bezeichnung": "Stadttour" }],
    "my_activities": [{ "id": 3, "bezeichnung": "Yoga im Park" }]
  }
  ```

- `GET /me/favorites`  
  List your favorite entries (id, aktivitaet_id, hinzugefuegt_am).

- `POST /me/favorites/{aktivitaet_id}`  
  Add an activity to your favorites.

- `DELETE /me/favorites/{aktivitaet_id}`  
  Remove a favorite.

- Reviews, plans and reminders endpoints also available under `/me` (see router for details):
  - `/me/reviews` (GET/POST/DELETE)
  - `/me/plans` (GET/POST/DELETE)
  - `/me/plans/{plan_id}/reminders` (GET/POST)
  - `/me/reminders/{reminder_id}` (DELETE)

## Activities & Locations

- `GET /activities` and other activity endpoints are available under `/activities` (see `app/Routers/activities.py`).
- `GET /locations` etc. under `/locations`.

## DB helpers

- `reset_db.py` clears most tables (keeps schema) — useful for development.
- `seed_users.py` seeds a test user and a test provider.

## Notes

- Secrets: `app/auth.py` contains a `SECRET_KEY` constant. For production change it and keep it secret.
- Passwords are hashed using `pbkdf2_sha256` via `passlib`.
- Login expects form-encoded OAuth2 compatible body (FastAPI `OAuth2PasswordRequestForm`). Many clients send `application/x-www-form-urlencoded` when using password grant.

If you want, I can also:
- Add a small `/auth/me` endpoint that returns the logged in user's details.
- Expand returned activity details in `/me/profile` to include location and time info.
>>>>>>> Backend
