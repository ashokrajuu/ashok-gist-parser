## GitHub Gists Parser - API Server

This project provides a simple HTTP web server API built with Python and Flask that fetches and returns a list of publicly available Gists for a specified GitHub user. It includes in-memory caching for performance, pagination support, automated tests, and is packaged in a Docker container.

![](static/gist1.png)

## Table of Contents

1. [GitHub Gists Parser - API Server](#github-gists-parser---api-server)
2. [Features](#features)
3. [Prerequisites](#prerequisites)
4. [Setup and Installation](#setup-and-installation)
   - [Option 1: Running with Docker](#option-1-running-with-docker)
   - [Option 2: Running Locally (Without Docker)](#option-2-running-locally-without-docker)
5. [Usage](#usage)
6. [Run Tests](#run-tests)
   - [Testing](#testing)
7. [Notes](#notes)
8. [Troubleshooting](#troubleshooting)


### Features

Endpoint:
```
GET /<username>?page=<page>&per_page=<per_page>
```
* Returns a JSON response with a paginated list of public Gists for the specified GitHub user.
* Supports pagination via query parameters page (default: 1) and per_page (default: 5).
* Uses in-memory caching to reduce GitHub API calls (cache TTL: 60 seconds).

Response Format:
```
{
  "gists": [
    {
      "created_at": "2014-10-01T16:19:34Z",
      "description": "Hello world!",
      "filename": [
        "hello_world.rb"
      ],
      "html_url": "https://gist.github.com/octocat/6cad326836d38bd3a7ae",
      "id": "6cad326836d38bd3a7ae",
      "owner": "octocat",
      "public": true
    }
  ],
  "page": 1,
  "per_page": 1,
  "total": 8,
  "total_pages": 8
}
```




> Returns an empty gists list ([]) for non-existent users or errors.


### Prerequisites

- Docker: Required to build and run the container.
- Python 3.9+ (optional): Only needed for local execution without Docker.
- GitHub API Access: No authentication required for public Gists; ensure internet access to query api.github.com.

#### Setup and Installation

##### Option 1: Running with Docker
Clone the Repository (or copy the project files to a directory):


> git clone <repository-url>
> 
> cd <repository-directory>

Build the Docker Image:

> docker build -t gists-parser-api .

Run the Docker Container:

> docker run -p 8080:8080 gists-parser-api

The API will be available at http://127.0.0.1:8080/<username>, e.g., http://127.0.0.1:8080/octocat?page=1&per_page=5

##### Option 2: Running Locally (Without Docker)

Install Dependencies: Ensure Python 3.9+ is installed, then install required packages:

> pip install -r requirements.txt

Run the Application:

> python gistcheck.py

The API will be available at http://127.0.0.1:8080/<username>.



### Usage
**Endpoint:** `GET /<username>`  
**Example:**  
```bash
curl http://127.0.0.1:8080/octocat
```
**Endpoint:** `GET /<username>?page=<page>&per_page=<per_page>`  
**Example:**  
```bash
curl http://127.0.0.1:8080/octocat?page=1&per_page=5
```

> For non-existent users or errors, gists is [] and total is 0.

### Run Tests:

#### Testing

The automated tests in testGistscp.py validate:
- User Gists: The /octocat endpoint returns a list of gists with correct pagination metadata.
- Non-existent User: The /nonexistentuser123456789 endpoint returns an empty list and total=0.
- Caching: Subsequent requests for the same user hit the in-memory cache.
- Pagination: Different page and per_page values return correct subsets of gists with consistent total.

Run tests with:

> python -m pytest test_Gists.py -v

or 

If pytest installed as system package,
> pytest -v

Example test output:
```
============================= test session starts ==============================
platform linux -- Python 3.12.3, pytest-8.3.3, pluggy-1.6.0
rootdir: /path/to/project
collected 4 items

testGistscpo.py::test_get_user_gists[octocat-1-5] PASSED               [ 25%]
testGistscpo.py::test_get_user_gists[nonexistentuser123456789-1-5] PASSED [ 50%]
testGistscpo.py::test_cache_behavior PASSED                            [ 75%]
testGistscpo.py::test_pagination PASSED                                [100%]

============================== 4 passed in 0.60s ===============================
```

### Notes
- GitHub API: Uses https://api.github.com/users/<username>/gists. Unauthenticated requests are limited to 60 per hour per IP.
- Caching: In-memory cache stores responses for 60 seconds to reduce API calls.
- Pagination: Supports page and per_page query parameters (defaults: page=1, per_page=5).
- Docker: The container listens on port 8080 and requires no external dependencies beyond Python.
- Dependencies: Minimal dependencies (flask, requests, pytest) to keep the solution simple.
- No System Changes: The solution avoids global system modifications and runs self-contained.

### Troubleshooting
- Network Issues: Ensure internet access for GitHub API calls. Rate limits (60 requests/hour) may cause 403 errors; the cache helps mitigate this.
- Test Failures: Check testGistscpo.py output for details. Ensure gistcheckcp.py and testGistscpo.py are in the same directory.
- Docker: If tests fail in Docker, run docker run github-gists-api pytest testGistscpo.py -v to debug.


