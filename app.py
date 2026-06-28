from flask import Flask, render_template, request, redirect
import sqlite3
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TMDB_API_KEY = os.getenv("TMDB_API_KEY")
TMDB_BASE_URL = "https://api.themoviedb.org/3"
POSTER_BASE_URL = "https://image.tmdb.org/t/p/w500"


def init_db():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            genre TEXT,
            status TEXT,
            rating INTEGER,
            notes TEXT,
            release_date TEXT,
            overview TEXT,
            poster_url TEXT,
            tmdb_rating REAL
        )
    """)

    conn.commit()
    conn.close()
    
init_db()

def fetch_movie(title):
    url = f"{TMDB_BASE_URL}/search/movie"

    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }

    response = requests.get(url, params=params)
    data = response.json()

    if data["results"]:
        movie = data["results"][0]

        poster_path = movie.get("poster_path")
        poster_url = f"{POSTER_BASE_URL}{poster_path}" if poster_path else ""

        return {
            "title": movie.get("title"),
            "release_date": movie.get("release_date"),
            "overview": movie.get("overview"),
            "poster_url": poster_url,
            "tmdb_rating": movie.get("vote_average")
        }

    return None


@app.route("/")
def home():
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM movies ORDER BY id DESC")
    movies = cursor.fetchall()
    conn.close()

    return render_template("index.html", movies=movies)


@app.route("/add", methods=["POST"])
def add_movie():
    title = request.form["title"]
    genre = request.form["genre"]
    status = request.form["status"]
    rating = request.form["rating"]
    notes = request.form["notes"]

    movie_data = fetch_movie(title)

    release_date = ""
    overview = ""
    poster_url = ""
    tmdb_rating = ""

    if movie_data:
        title = movie_data["title"]
        release_date = movie_data["release_date"]
        overview = movie_data["overview"]
        poster_url = movie_data["poster_url"]
        tmdb_rating = movie_data["tmdb_rating"]

    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO movies (
            title, genre, status, rating, notes,
            release_date, overview, poster_url, tmdb_rating
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        title, genre, status, rating, notes,
        release_date, overview, poster_url, tmdb_rating
    ))

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/delete/<int:movie_id>")
def delete_movie(movie_id):
    conn = sqlite3.connect("movies.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM movies WHERE id = ?", (movie_id,))
    conn.commit()
    conn.close()

    return redirect("/")


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", debug=True)
