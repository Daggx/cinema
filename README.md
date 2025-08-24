# 🎬 Cinema App

A Django REST API for managing films, authors (directors or writers), spectators, ratings, and favorites. The project uses **TMDb API** to populate movies and directors

---

## Setup & Installation

1. **Start the project with Docker Compose**

   ```bash
   docker compose -f ./docker-compose.yml up
   ```

2. **Enter the running container**

   ```bash
   docker exec -it cinema bash
   ```

3. **Create a superuser**

   ```bash
   python app/manage.py createsuperuser
   ```

4. **Access Django Admin**
   Go to [http://localhost:8000/admin](http://localhost:8000/admin) and log in with your superuser credentials

---

## Populate the Database with Movies & Authors

1. **Set your TMDb API key**

   * Create a free account on [TMDb](https://www.themoviedb.org/).
   * Add your API key to the `.env.dev` file.

2. **Add a single movie by TMDb ID**

   ```bash
   python app/manage.py add_movie {tmdb_movie_id}
   ```

   To insert the movie data and its director into the database

3. **Populate with popular movies (first page of TMDb popular list)**

   ```bash
   python app/manage.py populate_db
   ```
 TO insert the first page of the most popular movies from tmdb with their directors
---

## API Endpoints

### Authentication  

* `POST /register/` → Register a spectator
* `POST /login/` → Login and get the token token
* `POST /logout/` → Logout spectator
* `POST /refresh/` → Refresh JWT token

### Favorites & Ratings

* `GET /favorites/films/` → List favorite films
* `POST /favorites/films/<film_id>/add/` → Add a film to favorites
* `DELETE /favorites/films/<film_id>/remove/` → Remove a film from favorites
* `POST /films/<film_id>/rate/` → Rate a film
* `POST /authors/<author_id>/rate/` → Rate an author

### Films

* `GET /films/` → List all films (Public)
* `GET /films/<year>/` → Filter films by year
* `GET /films/<id>/` → Retrieve a film by id
* `PATCH /films/<id>/` → Update a film
* `DELETE /films/<id>/` → Delete a film


### Authors

* `GET /authors/` → List all authors ( Public)
* `GET /authors/<id>/` → Retrieve an author
* `PATCH /authors/<id>/` → Update an author
* `DELETE /authors/<id>/` → delete an author

---

# Testing Guide

**Base URL:** `http://localhost:8000/api/`
**Auth:** JWT (Bearer token)
**Admin credentials:** the superuser you created with `python app/manage.py createsuperuser`

---

## 1) Register a spectator

### Python

```python
import requests

url = "http://localhost:8000/api/register/"
payload = {
    "first_name": "name",
    "last_name": "last name",
    "email": "test@mail.com",
    "password": "Password1234"
}
r = requests.post(url, json=payload)
print(r.json())
```
---

## 2) Login to get your JWT token

You can log in with:

* **Admin (superuser)** → use this account to test admin only endpoints.
* **Spectator (regular user)** → use this account to test spectator features (favorites, ratings, etc.) .

The login response will return two tokens:

* `access` → used in the `Authorization` header for requests.
* `refresh` → used to get a new access token when it expires.

### Python

```python
import requests

url = "http://localhost:8000/api/login/"
payload = {
  "email": "ADMIN_EMAIL@domain.com",
  "password": "ADMIN_PASSWORD"
}
r = requests.post(url, json=payload)
tokens = r.json()
access = tokens["access"]
refresh = tokens["refresh"]
```
---

## 3) Use the token on protected endpoints

Add this HTTP header to every protected request:

```
Authorization: Bearer <ACCESS_TOKEN>
```

In Python:

```python
headers = {"Authorization": f"Bearer {access}"}
```

In cURL:

```bash
-H "Authorization: Bearer $ACCESS"
```

---

## 4) Public endpoints (no token)

### List authors

```python
import requests
print(requests.get("http://localhost:8000/api/authors/").json())
```

### List films

```python
import requests
print(requests.get("http://localhost:8000/api/films/").json())
```

---

## 5) Filter films by year (protected if your view requires auth; otherwise public)

```python
import requests
url = "http://localhost:8000/api/films/2002/"
r = requests.get(url, headers=headers)
print(r.json())
```

---

## 6) Get / Update / Delete single resources

### Get film by ID

```python
import requests
r = requests.get("http://localhost:8000/api/films/1/", headers=headers)
print(r.json())
```

### Patch (update) film

```python
import requests
url = "http://localhost:8000/api/films/1/"
r = requests.patch(url, headers=headers, json={"description": "Movie description updated"})
print(r.json())
```

### Delete author (admin-only)

```python
import requests
r = requests.delete("http://localhost:8000/api/authors/3/", headers=headers)
print(r.status_code, r.text)
```
---

## 7) Favorites (spectator & admin)

### Add favorite film

```python
import requests
url = "http://localhost:8000/api/favorites/films/1/add/"
r = requests.post(url, headers=headers)
print(r.json())
```

### List favorite films (spectator)

```python
import requests
url = "http://localhost:8000/api/favorites/films/"
r = requests.get(url, headers=headers)
print(r.json())
```

### Remove favorite film (spectator)

```python
import requests
url = "http://localhost:8000/api/favorites/films/1/remove/"
r = requests.delete(url, headers=headers)
print(r.json())
```

---

## 8) Ratings (spectator)

### Rate a film

```python
import requests
url = "http://localhost:8000/api/films/1/rate/"
r = requests.post(url, headers=headers, json={"note": 5})
print(r.json())
```

### Rate an author (spectator)

```python
import requests
url = "http://localhost:8000/api/authors/1/rate/"
r = requests.post(url, headers=headers, json={"note": 5})
print(r.json())
```

---

## 9) Refresh your access token (logged user)

When the access token expires, use your refresh token to get a new one.

### Python

```python
import requests
url = "http://localhost:8000/api/refresh/"
r = requests.post(url, json={"refresh": refresh})
new_access = r.json()["access"]
```