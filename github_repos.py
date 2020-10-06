from datetime import datetime
from github import Github
import csv
import time

timestr = time.strftime("%Y%m%d-%H%M%S")
token = ""
orgs = {
    1: "Pivotal",
    2: "Pivotal-DataFabric",
    3: "Pivotal-Data-Engineering",
    4: "Pivotal-Field-Engineering",
    5: "Pivotal-Gemfire",
    6: "pivotalsoftware",
    7: "GemXD",
    8: "Pivotal-gss",
    9: "Pivotal-cf",
}

print('Select a Org:\n'
      " 1. Pivotal\n",
      "2. Pivotal-DataFabric\n",
      "3. Pivotal-Data-Engineering\n",
      "4. Pivotal-Field-Engineering\n",
      "5. Pivotal-Gemfire\n",
      "6. pivotalsoftware\n",
      "7. GemXD\n",
      "8. Pivotal-gss\n",
      "9. Pivotal-cf\n",
      "10. All\n",
      "11. vmware-tanzu-private\n"
      )
org = int(input().strip())
filename = f'github-{orgs[org]}-{timestr}.csv'

github = Github(token)
g = github.get_organization(orgs[org])

print(f'Organization: {orgs[org]}')

def commit_info(repo):
    try:
        commit = repo.get_commits()[0]
        str_date = datetime.strptime(commit.last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        last_modified = f'{str_date.date()}-{str_date.time()}'

        try:
            return f'{commit.author.name} ({commit.author.login})', last_modified
        except:
            return "N/A", last_modified
    except:
        return "N/A", "N/A"


def contributor_info(repo):
    contributor_count = repo.get_contributors().totalCount

    if contributor_count == 0:
        return "N/A", "N/A"
    elif contributor_count == 1:
        return f'{repo.get_contributors()[0].name} ({repo.get_contributors()[0].login})', "N/A"
    else:
        return f'{repo.get_contributors()[0].name} ({repo.get_contributors()[0].login})', f'{repo.get_contributors()[1].name} ({repo.get_contributors()[1].login})'


def is_forked(repo):
    if repo.forks:
        return True
    else:
        return False


with open(filename, 'w') as f:
    writer = csv.writer(f)

    fields = [
        'Repository Link',
        'Github Org',
        'Repository Name',
        'Private',
        'Forked',
        'Archived',
        'Last Updated',
        'Last Commiter',
        'Top Committer',
        'Second Top Committer',
        'Owner'
    ]
    writer.writerow(fields)

    repos = g.get_repos()
    count = repos.totalCount
    print(f"Number of repos: {count}")
    
    for repo in repos:
        print(f"Working on: {repo.name}\r",  end="", flush=True)
        last_commit_author, last_commit_datetime = commit_info(repo)
        top_contributor, second_top_contributor = contributor_info(repo)
        forked = is_forked(repo)

        rows = [
            repo.html_url,
            repo.organization.name,
            repo.name,
            repo.private,
            forked,
            repo.archived,
            last_commit_datetime,
            last_commit_author,
            top_contributor,
            second_top_contributor,
            repo.owner.name
        ]

        writer.writerow(rows)
