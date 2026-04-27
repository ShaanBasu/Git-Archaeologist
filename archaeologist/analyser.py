from collections import Counter, defaultdict
import git

def analyse_repo(repo_path: str) -> dict:
    repo = git.Repo(repo_path)
    file_commits = Counter()
    file_authors = defaultdict(set)
    file_dates = defaultdict(list)

    scanned = 0
    for commit in repo.iter_commits(max_count=200):
        scanned += 1
        date = commit.committed_datetime
        for file in commit.stats.files:
            file_commits[file] += 1
            file_authors[file].add(commit.author.name)
            file_dates[file].append(date)

    hotspots = []
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