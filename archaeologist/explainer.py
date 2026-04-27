"""
This script provides all the necessary information to ollama and asks it to analyse it using a prompt. 
Note: You can change the prompt to make it give more summarised or detailed information according to your needs
"""

import requests

DEFAULT_MODEL = "llama3.2"
OLLAMA_URL = "http://localhost:11434/api/generate"
REQUEST_TIMEOUT = 60  # seconds

def explain_file(file_history: dict, model: str = DEFAULT_MODEL) -> str:
    commits = file_history.get("commits", [])
    
    if not commits:
        return "No commit history found for this file."

    commits_text = "\n".join([
        f"- [{c['date'][:10]}] {c['author']}: {c['message']}"
        for c in commits[:15]
    ])
    
    file_name = file_history.get('file', 'unknown file')
    prompt = f"""You are a code historian. Given this git history for '{file_name}', \
explain in detail: why this file exists, what problems it has solved(write the possibilities/conclusions of what problems has been solved), \
and any patterns you notice (e.g. repeated fixes, ownership changes, instability).

Commit history:
{commits_text}

Be specific and concise. No filler phrases."""

    try:
        response = requests.post(
            OLLAMA_URL,
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()  # catches 4xx and 5xx HTTP errors
        
        data = response.json()
        
        if "response" not in data:
            return f"Unexpected response from Ollama: {data}"
        
        return data["response"]

    except requests.exceptions.ConnectionError:
        return "Could not connect to Ollama. Make sure it's running: `ollama serve`"
    except requests.exceptions.Timeout:
        return f"Ollama took longer than {REQUEST_TIMEOUT}s to respond. Try a smaller model."
    except requests.exceptions.HTTPError as e:
        return f"Ollama returned an error: {e}"
    except (ValueError, KeyError) as e:
        return f"Failed to parse Ollama response: {e}"