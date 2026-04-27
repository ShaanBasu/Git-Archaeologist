# cli.py
import click
from archaeologist.extractor import extract_file_history
from archaeologist.explainer import explain_file

@click.command()
@click.argument("repo_path")
@click.argument("file_path")
def explain(repo_path, file_path):
    """Explain the history of a file in a git repo."""
    history = extract_file_history(repo_path, file_path)
    explanation = explain_file(history)
    click.echo(explanation)

if __name__ == "__main__":
    explain()