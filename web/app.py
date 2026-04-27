import os
import git
from flask import Flask, jsonify, request
from flask import render_template
from flask_cors import CORS
from collections import Counter
from archaeologist.extractor import extract_file_history
from archaeologist.analyser import analyse_repo
from archaeologist.explainer import explain_file

app = Flask(__name__, template_folder="templates", static_folder="static")
CORS(app)  # allows the frontend JS to call these endpoints without browser blocking


def validate_repo(repo_path: str):
    """Returns (repo, error_string). error_string is None if repo is valid."""
    if not repo_path:
        return None, "No repo_path provided."
    if not os.path.exists(repo_path):
        return None, f"Path does not exist: {repo_path}"
    try:
        repo = git.Repo(repo_path)
        return repo, None
    except git.InvalidGitRepositoryError:
        return None, f"Not a valid git repository: {repo_path}"
    except Exception as e:
        return None, f"Could not open repository: {str(e)}"


def is_safe_repo_file(repo_path: str, file_path: str) -> tuple:
    """
    Verifies that file_path resolves to a file inside repo_path (no path traversal).
    Returns (is_safe: bool, full_path: str, error: str).
    """
    repo_path = os.path.abspath(os.path.normpath(repo_path))
    full_path = os.path.abspath(os.path.join(repo_path, file_path))
    
    # Make sure the file path doesn't escape the repo (no path traversal attacks)
    try:
        os.path.commonpath([repo_path, full_path])
    except ValueError:
        return False, full_path, "Path traversal detected: file is outside repository."
    
    if not full_path.startswith(repo_path):
        return False, full_path, "File path escapes repository boundary."
    
    if not os.path.isfile(full_path):
        return False, full_path, f"Path is not a file: {file_path}"
    
    return True, full_path, None


def get_file_tree(repo_path: str) -> list:
    """Returns a flat list of all tracked text files in the repo."""
    # File extensions to skip (binary files and generated code)
    BINARY_EXTENSIONS = {
        ".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".pyc",
        ".db", ".sqlite", ".zip", ".tar", ".exe", ".whl", ".so",
        ".dll", ".bin", ".lock"
    }
    files = []
    for root, dirs, filenames in os.walk(repo_path):
        # Skip hidden and build directories to avoid noise
        dirs[:] = [
            d for d in dirs
            if not d.startswith(".")
            and d not in {"node_modules", "__pycache__", "venv", ".venv", "dist", "build"}
        ]
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, repo_path).replace("\\", "/")
            ext = os.path.splitext(filename)[1].lower()
            if ext not in BINARY_EXTENSIONS:
                files.append(rel_path)
    return sorted(files)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/load", methods=["POST"])
def load_repo():
    # Load a repository and return its file tree for the frontend
    """
    Load a repo and return its file tree.
    Body: { "repo_path": "C:/path/to/repo" }
    Returns: { "files": [...], "repo_name": "..." }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    repo_path = data.get("repo_path", "").strip()
    _, error = validate_repo(repo_path)
    if error:
        return jsonify({"error": error}), 400

    try:
        files = get_file_tree(repo_path)
        repo_name = os.path.basename(os.path.normpath(repo_path))
        return jsonify({
            "repo_name": repo_name,
            "repo_path": repo_path,
            "files": files,
            "file_count": len(files)
        })
    except Exception as e:
        return jsonify({"error": f"Failed to read file tree: {str(e)}"}), 500


@app.route("/api/analyse", methods=["POST"])
def analyse():
    # Analyze the entire repository to find hotspots (most changed files)
    """
    Run hotspot analysis on the whole repo.
    Body: { "repo_path": "C:/path/to/repo" }
    Returns: { "hotspots": [...], "total_commits_scanned": N }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    repo_path = data.get("repo_path", "").strip()
    _, error = validate_repo(repo_path)
    if error:
        return jsonify({"error": error}), 400

    try:
        result = analyse_repo(repo_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500


@app.route("/api/explain", methods=["POST"])
def explain():
    # Get detailed history and AI explanation for a specific file
    """
    Get git history + AI explanation for a specific file.
    Body: { "repo_path": "C:/path/to/repo", "file_path": "src/auth.py" }
    Returns: { "explanation": "...", "commits": [...], "file": "..." }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    repo_path = data.get("repo_path", "").strip()
    file_path = data.get("file_path", "").strip()

    if not file_path:
        return jsonify({"error": "No file_path provided."}), 400

    _, error = validate_repo(repo_path)
    if error:
        return jsonify({"error": error}), 400

    # Verify the file exists and is inside the repo (security check)
    is_safe, full_path, safety_error = is_safe_repo_file(repo_path, file_path)
    if not is_safe:
        return jsonify({"error": safety_error}), 400

    try:
        history = extract_file_history(repo_path, file_path)

        if not history["commits"]:
            return jsonify({
                "file": file_path,
                "commits": [],
                "explanation": "No commit history found for this file. It may be untracked or new."
            })

        explanation = explain_file(history)

        return jsonify({
            "file": file_path,
            "commits": history["commits"],
            "commit_count": len(history["commits"]),
            "explanation": explanation
        })

    except Exception as e:
        return jsonify({"error": f"Failed to explain file: {str(e)}"}), 500


@app.route("/api/stats", methods=["POST"])
def repo_stats():
    # Get overall repository statistics for the dashboard
    """
    Returns high-level repo stats for the dashboard header.
    Body: { "repo_path": "C:/path/to/repo" }
    Returns: { "total_commits": N, "total_authors": N, "top_authors": [...] }
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON."}), 400

    repo_path = data.get("repo_path", "").strip()
    repo, error = validate_repo(repo_path)
    if error:
        return jsonify({"error": error}), 400

    try:
        author_counts = Counter()
        total = 0

        # Count commits by author across the repo history
        for commit in repo.iter_commits(max_count=500):
            author_counts[commit.author.name] += 1
            total += 1

        # Get the top 5 contributors
        top_authors = [
            {"name": name, "commits": count}
            for name, count in author_counts.most_common(5)
        ]

        return jsonify({
            "total_commits": total,
            "total_authors": len(author_counts),
            "top_authors": top_authors
        })

    except Exception as e:
        return jsonify({"error": f"Failed to get repo stats: {str(e)}"}), 500


if __name__ == "__main__":
    app.run(debug=False, port=5000)