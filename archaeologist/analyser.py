"""
This Script analyses the repo and returns information regarding the repo and its files on a whole
"""

from collections import Counter, defaultdict
import git

def analyse_repo(repo_path: str) -> dict:
    #Create a repo object using the repo path
    repo = git.Repo(repo_path)
    # We then use 3 different variables to store different information from the repo
    file_commits = Counter()
    file_authors = defaultdict(set)
    file_dates = defaultdict(list)

    #We use this scanned variable to record the number of commits which we actually go through (for small repos with a small number of commits)
    scanned = 0
    for commit in repo.iter_commits(max_count=200): #we check through upto 200 commits of the repo 
        scanned += 1
        date = commit.committed_datetime
        #We then put all of the information of the commit into the variables created.
        for file in commit.stats.files:
            file_commits[file] += 1
            file_authors[file].add(commit.author.name)
            file_dates[file].append(date)

    hotspots = [] # We use this to record the top 10 files in the repo which have the most amount of commits done to them
    for f, c in file_commits.most_common(10):
        dates = sorted(file_dates[f])
        # days between first and last commit touching this file
        lifespan_days = (dates[-1] - dates[0]).days if len(dates) > 1 else 1
        # changes per day — high value = file is being thrashed
        churn_rate = round(c / max(lifespan_days, 1), 3) 

        hotspots.append({
            "file": f,
            "changes": c,
            "authors": len(file_authors[f]),
            "churn_rate": churn_rate,
            "first_changed": dates[0].isoformat(),
            "last_changed": dates[-1].isoformat(),
        })

    return {"hotspots": hotspots, "total_commits_scanned": scanned}