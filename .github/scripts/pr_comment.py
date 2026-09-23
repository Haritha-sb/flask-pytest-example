"""Post (or update) the test-results table as a comment on the pull request."""
import json
import os
import sys
import urllib.request

from junit_summary import MARKER, render

API = 'https://api.github.com'


def call(url, token, method='GET', payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header('Authorization', 'Bearer %s' % token)
    request.add_header('Accept', 'application/vnd.github+json')
    if data:
        request.add_header('Content-Type', 'application/json')
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read() or b'{}')


def existing_comment_id(repo, pr, token):
    """Find the comment this workflow posted on an earlier run, if any."""
    comments = call('%s/repos/%s/issues/%s/comments?per_page=100' % (API, repo, pr), token)
    for comment in comments:
        if comment.get('body', '').startswith(MARKER):
            return comment['id']
    return None


def main(xml_path):
    token = os.environ['GH_TOKEN']
    repo = os.environ['GITHUB_REPOSITORY']
    pr = os.environ['PR_NUMBER']

    body = {'body': render(xml_path)}
    comment_id = existing_comment_id(repo, pr, token)
    if comment_id:
        call('%s/repos/%s/issues/comments/%s' % (API, repo, comment_id), token, 'PATCH', body)
        print('updated comment %s on PR #%s' % (comment_id, pr))
    else:
        call('%s/repos/%s/issues/%s/comments' % (API, repo, pr), token, 'POST', body)
        print('created comment on PR #%s' % pr)


if __name__ == '__main__':
    main(sys.argv[1])
