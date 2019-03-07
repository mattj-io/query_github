#!/usr/bin/env python

from github import Github, GithubException
import datetime
import argparse
import csv
import xlsxwriter

def get_public_repos(organization):
    '''
    Return a list of public repos which aren't forks
    '''
    public_repos = gh.get_organization(organization).get_repos('public')
    for repo in public_repos:
        if not repo.fork:
            yield repo

def get_org_members(organization):
    '''
    Return a list of member logins
    '''
    org_mems = []
    org = gh.get_organization(organization).get_members()
    for member in org:
        org_mems.append(member.login)
    return org_mems

def get_private_repos(organization):
    '''
    Return a list of private repos in an org
    which aren't forks
    '''
    private_repos = gh.get_organization(organization).get_repos('private')
    for repo in private_repos:
        if not repo.fork:
            yield repo
    
def get_forked_repos(organization):
    '''
    Return a list of public repos in an org
    which are forks
    '''
    forks = gh.get_organization(organization).get_repos('public')
    for repo in forks:
        if repo.fork:
            yield repo

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

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="Github API token", action="store", dest="token", required=True)
    parser.add_argument("-o", "--org", help="Github organisation", action="store", dest="org", required=True)
    parser.add_argument("-a", "--additionalorg", help="Additional Github organisation to check for members", action="store", dest="addorg")
    parser.add_argument("--forks", help="include forks", action="store_true", default=False) 
    parser.add_argument("--public", help="include public repos", action="store_true", default=False) 
    parser.add_argument("--private", help="include private repos", action="store_true", default=False) 
    args = parser.parse_args()
    
    # FIXME output csv
    # FIXME output spreadsheet
    # FIXME clone the repo and check for LICENSE, CONTRIBUTING and README then delete
    # FIXME create class
    # FIXME output table
    # FIXME handle private forks
    # FIXME add archive code - download, tar and push to Amazon glacier

    # Setup Github connection
    gh = Github(args.token)
    # Populate members list
    members = get_org_members(args.org)
    if args.addorg:
        members += get_org_members(args.addorg)
    # Remove any duplicates
    org_mems = list(set(members))
    # Gather the repos we need
    repos = []
    if args.public:
        repos += get_public_repos(args.org)
    if args.private:
        repos += get_private_repos(args.org)
    # Build output data
    for repo in repos:
            # Catch empty repos
            try:
                repo.get_contents("/")
            except GithubException as e:
                continue
            issue_count, open_prs, perms, commit_age = get_repo_meta(repo, org_mems)
            print "%s,%s,%s,%s,%i,%s,%i" % (repo.clone_url, perms, open_prs, issue_count, repo.forks_count, repo.pushed_at.strftime('%m/%d/%Y'), commit_age)
