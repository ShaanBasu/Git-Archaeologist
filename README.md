# Git Archaeologist v1.0

A web-based Git repository analysis tool that uncovers the history and patterns of your codebase. Identify hotspots (frequently changed files), visualize commit patterns, and get AI-powered insights into why files exist and how they've evolved.

## Features

- **Hotspot Analysis**: Identify the top 10 most frequently changed files in your repository with churn rate metrics
- **Commit Visualization**: Interactive charts showing commit frequency over time for any file
- **AI Explanations**: Uses Ollama to provide AI-generated analysis of file history and purpose (optional)
- **File Browser**: Browse all files in your repository or filter by name
- **Repository Statistics**: View total commits, unique authors, and top contributors
- **Secure Path Handling**: Protected against path traversal attacks
- **Dark Mode UI**: Modern terminal-inspired design with real-time status updates

## Prerequisites

- **Python 3.8+**
- **Git** (must be installed and accessible from command line)
- **Ollama** (optional, for AI explanations) — [Download here](https://ollama.ai)

## Installation

### 1. Clone or download the project

```bash
git clone <repository-url>
cd "Git Archaeologist"
```

### 2. Create a virtual environment (optional but recommended)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
pip install -r requirements.txt
```

### 4. (Optional) Set up Ollama for AI explanations

If you want AI-powered file analysis:

```powershell
# Download and install Ollama from https://ollama.ai
# Then pull a model (e.g., llama2 or llama3.2)
ollama pull llama3.2
```

## Usage

### Starting the Application

**From project root:**

```powershell
python -m web.app
```

You should see:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: off
```

**Open your browser to:**
```
http://localhost:5000
```

### Using the Web Interface

1. **Enter a Repository Path**
   - Paste the full path to any local Git repository
   - Example: `C:\Users\you\projects\my-repo`
   - Click `SCAN` or press Enter

2. **View Repository Stats** (top bar)
   - **COMMITS**: Total commits scanned (up to 500)
   - **AUTHORS**: Unique contributors in the last 500 commits
   - **FILES**: Total text files in the repository

3. **Analyze Hotspots** (left panel, CHURN tab)
   - Files are ranked by "churn rate" (changes per day)
   - Color coding:
     - 🔴 Red: High churn (frequently changed, potentially unstable)
     - 🟡 Orange: Medium churn
     - 🟢 Green: Low churn (stable)
   - Shows number of commits and unique authors per file

4. **Browse All Files** (left panel, ALL FILES tab)
   - Search/filter files by name
   - Click any file to analyze

5. **File Analysis** (right panel)
   - **AI ANALYSIS**: AI-generated explanation of the file (requires Ollama)
   - **COMMIT FREQUENCY**: Chart showing when the file was changed
   - **COMMIT LOG**: Last 20 commits touching this file

### API Endpoints

All endpoints accept POST requests with JSON body and return JSON.

#### `POST /api/load`
Load a repository and list its files.

**Request:**
```json
{
  "repo_path": "C:\\path\\to\\repo"
}
```

**Response:**
```json
{
  "repo_name": "my-repo",
  "repo_path": "C:\\path\\to\\repo",
  "files": ["file1.py", "src/file2.js", ...],
  "file_count": 42
}
```

#### `POST /api/analyse`
Run hotspot analysis on the repository.

**Request:**
```json
{
  "repo_path": "C:\\path\\to\\repo"
}
```

**Response:**
```json
{
  "hotspots": [
    {
      "file": "src/core.py",
      "changes": 47,
      "authors": 5,
      "churn_rate": 0.235,
      "first_changed": "2023-01-15T10:30:00+00:00",
      "last_changed": "2024-03-20T14:45:00+00:00"
    }
  ],
  "total_commits_scanned": 200
}
```

#### `POST /api/stats`
Get repository-wide statistics.

**Request:**
```json
{
  "repo_path": "C:\\path\\to\\repo"
}
```

**Response:**
```json
{
  "total_commits": 342,
  "total_authors": 8,
  "top_authors": [
    { "name": "Alice", "commits": 142 },
    { "name": "Bob", "commits": 98 }
  ]
}
```

#### `POST /api/explain`
Get file history and AI explanation.

**Request:**
```json
{
  "repo_path": "C:\\path\\to\\repo",
  "file_path": "src/auth.py"
}
```

**Response:**
```json
{
  "file": "src/auth.py",
  "commits": [
    {
      "hash": "a1b2c3d4",
      "author": "Alice",
      "date": "2024-03-20T14:45:00+00:00",
      "message": "Refactor authentication logic",
      "diff": "@@ -10,3 +10,4 @@ ..."
    }
  ],
  "commit_count": 23,
  "explanation": "This file handles user authentication..."
}
```

## Project Structure

```
Git Arachaeologist/
├── web/                          # Flask web application
│   ├── app.py                   # Main Flask app & API routes
│   ├── templates/
│   │   └── index.html           # Web UI (HTML + JavaScript)
│   ├── static/
│   │   └── style.css            # Styling (dark mode theme)
│   └── __init__.py
├── archaeologist/                # Core analysis modules
│   ├── extractor.py             # Git history extraction
│   ├── analyser.py              # Hotspot analysis & churn metrics
│   ├── explainer.py             # AI explanations via Ollama
│   └── __init__.py
├── cli.py                        # Command-line interface (optional)
├── requirements.txt              # Python dependencies
├── .gitignore                    # Git ignore rules
└── README.md                     # This file
```

## How It Works

### 1. **Extraction** (`archaeologist/extractor.py`)
- Scans the last 50 commits touching a specific file
- Extracts commit metadata: hash, author, date, message
- Computes diffs (changes) for each commit
- Handles binary files gracefully

### 2. **Analysis** (`archaeologist/analyser.py`)
- Scans the last 200 commits across the entire repository
- Tracks which files were changed and how many times
- Records unique authors per file
- Computes "churn rate" = changes / days between first and last commit
- Returns top 10 hotspots ranked by churn rate

### 3. **Explanation** (`archaeologist/explainer.py`)
- Takes commit history and sends to Ollama
- Ollama runs a local LLM to generate insights
- Returns markdown text explaining the file's purpose and patterns
- Falls back gracefully if Ollama is unavailable

## Configuration

### Disable Debug Mode

In `web/app.py`, line 213:

```python
app.run(debug=False, port=5000)  # Already set to False
```

### Change Port

To run on a different port, edit the line above:

```python
app.run(debug=False, port=8000)  # Run on port 8000 instead
```

### Change Ollama Model

In `archaeologist/explainer.py`, line 3:

```python
DEFAULT_MODEL = "llama2"  # Change from llama3.2
```

Available models: `llama2`, `llama3`, `neural-chat`, `mistral`, etc. (install via `ollama pull <model>`)

## Troubleshooting

### **ModuleNotFoundError: No module named 'archaeologist'**

Make sure you're running from the project root with:
```powershell
python -m web.app
```

NOT:
```powershell
python web/app.py
```

### **"Could not connect to Ollama" message**

The app works without Ollama! You'll just get a connection error instead of AI explanations.

To enable Ollama:
```powershell
ollama serve
```

Then reload the file in the web interface.

### **Path not found error**

- Verify the repository path exists and is a valid Git repository
- Use forward slashes (/) or double backslashes (\\) in Windows paths
- Example: `C:/Users/snowl/Desktop/repo` or `C:\\Users\\snowl\\Desktop\\repo`

### **No hotspots found**

The repository may have fewer than 10 frequently changed files, or no commits in the scanned range. Try a larger repository like Flask or CPython.

### **Slow performance**

- Hotspot analysis scans 200 commits — this is slower on large repositories
- File explanation waits for Ollama — this can take 10-30 seconds depending on model size
- Consider using a smaller Ollama model (e.g., `neural-chat` instead of `llama3.2`)

## Security Notes

- ✅ Path traversal protection: Files outside the repo cannot be accessed
- ✅ Runs locally by default (no internet exposure)
- ✅ No stored credentials or sensitive data
- ⚠️ Debug mode is disabled in production
- ⚠️ If deploying to a server, add authentication and disable CORS

## Development

### Running tests (if added in future)

```powershell
pytest tests/
```

### Modifying the UI

Edit `web/templates/index.html` and `web/static/style.css`

### Adding new analysis features

Edit `archaeologist/analyser.py` or create new modules in the `archaeologist/` folder

## License

MIT License - Feel free to use this project for personal and commercial purposes.

## Contributing

Contributions welcome! Please:
1. Create a feature branch
2. Test your changes
3. Submit a pull request

## Contact & Support

For issues, questions, or suggestions, open an issue on the repository.

---

