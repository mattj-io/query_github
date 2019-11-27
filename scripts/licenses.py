#!/usr/bin/env python

from gh_query import get_public_repos, gh_login, get_org_members
import argparse
import os
import shutil
from git import Repo

tmp_path = '/tmp/gh_query'

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--token", help="Github API token", action="store", dest="token", required=True)
    parser.add_argument("-o", "--org", help="Github organisation", action="store", dest="org", required=True)
    args = parser.parse_args()

    # Setup Github connection
    gh = gh_login(args.token)
    missing_licenses = []
    # Gather all public repos
    repos = get_public_repos(gh, args.org)
    for repo in repos :
        # Make a scratch dir
        try:
            os.mkdir(tmp_path)
        except OSError:
            print ("Creation of the directory %s failed" % tmp_path)
            exit
        Repo.clone_from(repo.clone_url, tmp_path)
        if not os.path.isfile(tmp_path + '/' + 'LICENSE'):
            missing_licenses.append(repo)
        shutil.rmtree(tmp_path)
    print "The following repos are missing licenses"
    for repo in missing_licenses:
        print repo.clone_url, repo.pushed_at.strftime('%m/%d/%Y') 
