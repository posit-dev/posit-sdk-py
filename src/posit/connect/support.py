import urllib.parse

def create_github_issue_link(issue_title: str, issue_body: str):
    title = urllib.parse.quote(title)
    body = urllib.parse.quote(body)
    return f"https://github.com/posit-dev/posit-sdk-py/issues/new?title={title}&body={body}"
