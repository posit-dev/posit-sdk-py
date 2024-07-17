from posit.connect import support


def test_create_github_issue_link():
    issue_link = support.create_github_issue_link("title", "body")
    assert issue_link.startswith(
        "https://github.com/posit-dev/posit-sdk-py/issues/new"
    )
