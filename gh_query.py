from github import Github, GithubException
import datetime

def gh_login(token):
    """
    Login and return a Github connection
    """
    gh = Github(token)
    return gh

def get_public_repos(gh, organization):
    '''
    Return a generator of public repos which aren't forks
    '''
    public_repos = gh.get_organization(organization).get_repos('public')
    output_list = [ repo for repo in public_repos if not repo.fork ]
    return output_list

def get_org_members(gh, organization):
    '''
    Return a list of member logins
    '''
    org_mems = []
    org = gh.get_organization(organization).get_members()
    for member in org:
        org_mems.append(member.login)
    return org_mems

def get_private_repos(gh, organization):
    '''
    Return a generator of private repos in an org
    which aren't forks
    '''
    private_repos = gh.get_organization(organization).get_repos('private')
    output_list = [ repo for repo in public_repos if not repo.fork ]
    return output_list
    
def get_forked_repos(gh, organization):
    '''
    Return a list of public repos in an org
    which are forks
    '''
    forks = gh.get_organization(organization).get_repos('public')
    output_list = [ repo for repo in forks if repo.fork ]
    return output_list

def get_external_issues(repo, userlist):
    '''
    Return a list of issues in a repo
    created by users not in a list of users
    '''
    issues = [ issue for issue in repo.get_issues(state='open') if issue.user.login not in userlist and not hasattr(issue.pull_request, 'html_url') ]
    return issues

def get_external_issue_count(repo, userlist):
    '''
    Return a count of issues in a repo
    created by users not in a list of users
    '''
    issues = [ issue for issue in repo.get_issues(state='open') if issue.user.login not in userlist and not hasattr(issue.pull_request, 'html_url') ]
    return len(issues)

def get_external_prs(repo, userlist):
    '''
    Return a list of PR's in a repo
    created by users not in a list of users
    '''
    prs = [ pr for pr in repo.get_pulls(state='open') if pr.user.login not in userlist ]
    return prs

def get_external_pr_count(repo, userlist):
    '''
    Return a count of PR's in a repo
    created by users not in a list of users
    '''
    prs = [ pr for pr in repo.get_pulls(state='open') if pr.user.login not in userlist ]
    return len(prs)

def get_push_age(repo):
    '''
    Return number of days since last push
    Will include open PR's
    '''
    delta = datetime.date.today() - repo.pushed_at.date()
    return delta.days

def get_commit_age(repo):
    '''
    Return number of days since last commit
    '''
    delta = datetime.date.today() - repo.get_commits()[0].commit.committer.date.date()
    return delta.days

def get_repo_meta(repo, org_mems):
    if repo.has_issues:
        issue_count = get_external_issue_count(repo, org_mems)
    else:
        issue_count = 'n/a'
    if repo.private:
        perms = "Private"
    else:
        perms = "Public"
    commit_age = get_commit_age(repo)
    open_prs = get_external_pr_count(repo, org_mems)
    return (issue_count, open_prs, perms, commit_age)
