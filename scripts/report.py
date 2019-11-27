#!/usr/bin/env python

import gh_query
import argparse

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
    gh = gh_login(args.token)
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
    if args.forks:
        repos += get_forked_repos(args.org)
# Build output data
    for repo in repos:
            # Catch empty repos
            try:
                repo.get_contents("/")
            except GithubException as e:
                print "%s,%s" % (repo.clone_url, "Empty")
                continue
            if repo.fork:
                print "%s,%s" % (repo.clone_url, "Fork")
                continue
            issue_count, open_prs, perms, commit_age = get_repo_meta(repo, org_mems)
            print "%s,%s,%s,%s,%i,%s,%i" % (repo.clone_url, perms, open_prs, issue_count, repo.forks_count, repo.pushed_at.strftime('%m/%d/%Y'), commit_age)
