import json
import requests

BASE_URL = "https://api.themoviedb.org/3"


class TmdbAPI:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

    def get_popular_films(self, page: int = 1):
        url = f"{BASE_URL}/movie/popular"
        response = requests.get(url=url, headers=self.headers, params={"page": page})
        response.raise_for_status()
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise Exception("Internal server error")
        return data

    def get_film_details(self, film_id: str):
        url = f"{BASE_URL}/movie/{film_id}"
        response = requests.get(url=url, headers=self.headers)
        response.raise_for_status()
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise Exception("Internal server error")
        return data

    def get_people_detail(self, person_id: str):
        url = f"{BASE_URL}/person/{person_id}"
        response = requests.get(url=url, headers=self.headers)
        response.raise_for_status()
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise Exception("Internal server error")
        return data

    def get_movie_credits(self, film_id: str):
        url = f"{BASE_URL}/movie/{film_id}/credits"
        response = requests.get(url=url, headers=self.headers)
        response.raise_for_status()
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise Exception("Internal server error")
        return data
    
    
