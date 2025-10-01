from flask import Flask, jsonify, request, send_from_directory
import requests
import time
import os

app = Flask(__name__)

GITHUB_API_URL = "https://api.github.com/users/{}/gists"

# Simple in-memory cache: {username: (timestamp, data)}
CACHE = {}
CACHE_TTL = 60  # cache expiration in seconds


def fetch_gists(username):
    """Fetch gists from GitHub API for a given user."""
    try:
        response = requests.get(GITHUB_API_URL.format(username), timeout=10)
        if response.status_code == 200:
            gists = response.json()
            formatted = []
            for g in gists:
                filenames = list(g["files"].keys())
                formatted.append(
                    {
                        "id": g["id"],
                        "description": g["description"] or "No description",
                        "html_url": g["html_url"],
                        "public": g["public"],
                        "created_at": g["created_at"],
                        "owner": g["owner"]["login"] if g.get("owner") else None,
                        "filename": filenames,
                    }
                )
            return formatted, 200
        else:
            return [], response.status_code
    except requests.RequestException:
        return [], 500

@app.route("/")
def home():
    # Get absolute path of the static folder
    static_dir = os.path.join(os.path.dirname(__file__), "static")
    return send_from_directory(static_dir, "default.html")

@app.route("/health")
def health():
    return "OK", 200

@app.route('/favicon.ico')
def favicon():
    # return "", 204
    return send_from_directory('static', 'gist1.png')

@app.route("/<username>")
def get_user_gists(username):
    # Query params
    page = request.args.get("page")
    per_page = request.args.get("per_page")

    # Check cache
    cached = CACHE.get(username)
    if cached:
        ts, data = cached
        if time.time() - ts < CACHE_TTL:
            gists = data
        else:
            gists, status = fetch_gists(username)
            CACHE[username] = (time.time(), gists)
    else:
        gists, status = fetch_gists(username)
        CACHE[username] = (time.time(), gists)

    # If no pagination params → return all
    if page is None and per_page is None:
        paginated = gists
        page = 1
        per_page = len(gists)
    else:
        page = int(page or 1)
        per_page = int(per_page or 5)
        start = (page - 1) * per_page
        end = start + per_page
        paginated = gists[start:end]

    return (
        jsonify(
            {
                "page": page,
                "per_page": per_page,
                "total": len(gists),
                "gists": paginated,
                "total_pages": (len(gists) + per_page - 1) // per_page,
            }
        ),
        200,
    )


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
