""" 
This Script extracts the file history of the files in the repo and returns that information.
"""
import git


def extract_file_history(repo_path: str, file_path: str) -> dict:
    #Creating a repo object
    repo = git.Repo(repo_path)
    #Making a list of the commit history/information of the repo of max 50 commits
    commits = list(repo.iter_commits(paths= file_path, max_count = 50))
    
    history = []
    
    #We then use the commit of the list and extract structured data from it and place it inside the history dictionary
    for commit in commits:
        history.append({
            "hash": commit.hexsha[:8],
            "author": commit.author.name,
            "date": commit.committed_datetime.isoformat(),
            "message": commit.message.strip(),
            "diff": get_diff(repo, commit, file_path)
        })
    
    return {"file": file_path, "commits": history}

def get_diff(repo, commit, file_path):
    #If the commit has no parent just return empty string
    if not commit.parents:
        return ""
    
    try:
        diffs = commit.diff(commit.parents[0], paths=file_path)
        
        #If files are renamed the diff will be an empty list
        if not diffs:
            return ""
        
        diff_obj = diffs[0]
        
        #When files are binary their diff is set to None
        if diff_obj.diff is None:        
            return "[binary file — no text diff]"
        
        return diff_obj.diff.decode("utf-8", errors="replace")
        # errors="replace" swaps undecodable bytes with ? instead of crashing
    
    except (IndexError, UnicodeDecodeError, AttributeError, Exception):
        return ""      # silent fallback — one bad commit won't kill the whole run