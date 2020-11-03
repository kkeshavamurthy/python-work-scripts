import calendar
from datetime import datetime
from github import Github
from github import RateLimitExceededException
import csv
import time

token = ""
github = Github(token)

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
    10: "greenplum-db",
    11: "gemfire"
}

actions = {
    1: "Repos",
    2: "Members"
}


def what_to_do():
    print('Select a Org:\n'
          " 1. Pivotal\n",
          "2. Pivotal-DataFabric\n",
          "3. Pivotal-Data-Engineering\n",
          "4. Pivotal-Field-Engineering\n",
          "5. Pivotal-Gemfire\n",
          "6. Pivotalsoftware\n",
          "7. GemXD\n",
          "8. Pivotal-gss\n",
          "9. Pivotal-cf\n",
          "10.Greenplum-db\n",
          "11.Gemfire\n",
          )
    org = int(input().strip())

    print('Select Action:\n'
          " 1. Read Repos\n",
          "2. Get Members\n"
          )

    action = int(input().strip())

    return org, action


def setup_github(org, action):
    global g
    global filename

    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = f'github-{orgs[org]}-{actions[action]}-{timestr}.csv'

    g = github.get_organization(orgs[org])
    print(f'Organization: {orgs[org]}')


def commit_info(repo):
    try:
        commit = repo.get_commits()[0]
        str_date = datetime.strptime(commit.last_modified, '%a, %d %b %Y %H:%M:%S %Z')
        last_modified = f'{str_date.date()}'

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


def backoff():
    rate_limit = github.get_rate_limit().core
    reset_timestamp = calendar.timegm(rate_limit.reset.timetuple())
    # add 10 seconds to be sure the rate limit has been reset
    sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
    print(f"Github RateLimit Exceeded. Sleeping for {sleep_time}s\n")
    time.sleep(sleep_time)


def read_repos():
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
        repo_num = 1

        for repo in repos:
            try:
                print(f"{repo_num}.Working on: {repo.name}", end="\r", flush=True)
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
                repo_num = repo_num + 1

            except RateLimitExceededException:
                backoff()
                continue


def get_members():
    with open(filename, 'w') as f:
        writer = csv.writer(f)

        fields = [
            'Name',
            'Username',
            'Email'
        ]
        writer.writerow(fields)

        members = g.get_members()

        for member in members:
            try:
                print(f"Working on: {member.name}", end="\r", flush=True)
                rows = [
                    member.name if member.name else "N/A",
                    member.login,
                    member.email if member.email else "N/A",
                ]

                writer.writerow(rows)

            except RateLimitExceededException:
                backoff()
                continue


if __name__ == "__main__":

    org, action = what_to_do()
    setup_github(org, action)

    if action == 1:
        read_repos()

    elif action == 2:
        get_members()
