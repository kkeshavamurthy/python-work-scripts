import calendar
from datetime import datetime
from github import Github
from github import RateLimitExceededException
import csv
import time

token = ""
github = Github(token)

actions = {
    1: "Repos",
    2: "Members",
    3: "Teams",
    4: "Write"
}


def what_to_do():
    global write_repo_list
    global file_content
    global commit_message

    orgs = {
        1: "Pivotal",
        2: "Pivotal-DataFabric",
        3: "Pivotal-Data-Engineering",
        4: "Tanzu-Solution-Engineering",
        5: "Pivotal-Gemfire",
        6: "pivotalsoftware",
        7: "GemXD",
        8: "Pivotal-gss",
        9: "Pivotal-cf",
        10: "greenplum-db",
        11: "gemfire"
    }

    print('Select a Org:\n'
          " 1. Pivotal\n",
          "2. Pivotal-DataFabric\n",
          "3. Pivotal-Data-Engineering\n",
          "4. Tanzu-Solution-Engineering\n",
          "5. Pivotal-Gemfire\n",
          "6. Pivotalsoftware\n",
          "7. GemXD\n",
          "8. Pivotal-gss\n",
          "9. Pivotal-cf\n",
          "10.Greenplum-db\n",
          "11.Gemfire\n",
          "99.ENTER YOUR OWN\n",
          )
    org = int(input().strip())

    if org == 99:
        print("Enter Org Name:\n")
        org_name = str(input().strip())
    else:
        org_name = orgs[org]

    print('Select Action:\n'
          " 1. Read Repos\n",
          "2. Get Members\n",
          "3. Get Teams\n",
          "4. Write Repo\n"
          )

    action = int(input().strip())

    if action == 4:
        print('Enter content to update:\n')
        file_content = str(input())

        print('Enter Commit message:\n')
        commit_message = str(input().strip())

        print("Enter repos to update: (comma seperated)")
        write_repo_list = input().split(',')

    return org_name, action


def setup_github(org, action):
    global g
    global filename

    timestr = time.strftime("%Y%m%d-%H%M%S")
    filename = f'github-{org}-{actions[action]}-{timestr}.csv'

    g = github.get_organization(org)
    print(f'Organization: {org}')


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


def get_items(items):
    item_list = []

    try:
        if items.totalCount == 0:
            return "N/A"

        for item in items:
            item_list.append(item.name)

        return ",".join(item_list)

    except:
        return "N/A"


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
            'Teams'
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
                team_list = get_items(repo.get_teams())

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
                    team_list
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


def get_teams():
    with open(filename, 'w') as f:
        writer = csv.writer(f)

        fields = [
            'Team Name',
            'Repos'
        ]
        writer.writerow(fields)

        teams = g.get_teams()
        print(f'Total Teams: {teams.totalCount}')

        count = 1

        for team in teams:
            try:
                print(f"{count}. Working on: {team.name}", end="\r", flush=True)
                repo_list = get_items(team.get_repos())

                rows = [
                    team.name,
                    repo_list,
                ]

                writer.writerow(rows)
                count = count + 1

            except RateLimitExceededException:
                backoff()
                continue


def readme_exists(contents):
    for content in contents:
        if (content.type == 'file') and (content.name.lower() == "readme.md"):
            return content.path

    return None


def update_file(write_repo_list, file_content):
    for repo_name in write_repo_list:

        repo = g.get_repo(repo_name)
        contents = repo.get_contents("")
        readme_path = readme_exists(contents)

        if readme_path:
            file = repo.get_contents(readme_path)
            data = file.decoded_content.decode()
            updated_data = file_content + data

            print(f"Updating {readme_path} in {repo.name}...\n", end="")
            repo.update_file(readme_path, commit_message, updated_data, file.sha)
            print("Done.")

        else:
            print(f"Creating Readme.md in {repo.name}...", end="")
            repo.create_file("Readme.md", commit_message, file_content)
            print("Done.")


if __name__ == "__main__":

    org, action = what_to_do()
    setup_github(org, action)

    if action == 1:
        read_repos()

    elif action == 2:
        get_members()

    elif action == 3:
        get_teams()

    elif action == 4:
        update_file(write_repo_list, file_content)
