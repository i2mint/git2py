from functools import partial
import json
import os
import subprocess
import sys
import requests
from i2 import Sig

from git2py.gitlab import url_templates

GITHUB_BASE_URL = 'https://github.com'
GITHUB_API_BASE_URL = 'https://api.github.com'
DFLT_LOCAL_REPO_DIR = 'current_repo'


def git(*args):
    return subprocess.check_output(['git'] + list(args)).decode().strip()


def gitlab_api_get(gitlab_base_url, api_route, gitlab_token, **params):
    gitlab_api_url = os.path.join(gitlab_base_url, 'api', 'v4', api_route)
    _params = dict(params, per_page=100)
    headers={'PRIVATE-TOKEN': gitlab_token}
    page_nb = 1
    result = []
    while page_nb != 0:
        _params['page'] = page_nb
        page = requests.get(url=gitlab_api_url, params=_params, headers=headers).json()
        if page:
            result.extend(page)
            page_nb += 1
        else:
            page_nb = 0
    return result


def fetch_projects(gitlab_base_url, gitlab_token):
    print(f'Fetching projects from {gitlab_base_url} ...')
    api_route = url_templates['projects']
    gitlab_projects = gitlab_api_get(
        gitlab_base_url, 
        api_route,
        gitlab_token
    )
    gitlab_projects.sort(key=lambda x: x['path'].lower())
    print(f'Fetched {len(gitlab_projects)} projects')
    return gitlab_projects


def check_if_github_repo_exists(repo_name, github_org, github_token):
    github_api_repo_url = os.path.join(GITHUB_API_BASE_URL, 'repos', github_org, repo_name)
    headers = {'Authorization': f'Bearer {github_token}'}
    return requests.get(github_api_repo_url, headers=headers).status_code == 200
    

def migrate_repo(gitlab_repo_url, github_repo_url):
    print(f'Migrating {gitlab_repo_url} to {github_repo_url} ...')
    git('clone', '--mirror', gitlab_repo_url, DFLT_LOCAL_REPO_DIR)
    os.chdir(DFLT_LOCAL_REPO_DIR)
    git('push', '--no-verify', '--mirror', github_repo_url)


def main(gitlab_base_url, gitlab_token, github_org, github_token, name_map_str=None):
    name_map_str = name_map_str or '{}'
    name_map = json.loads(name_map_str)
    gitlab_projects = fetch_projects(gitlab_base_url, gitlab_token)
    migrated_project_count = 0
    # previous_repo_name = None
    # same_name_count = 1
    for project in gitlab_projects:
        repo_path = project['path_with_namespace']
        repo_name = name_map.get(repo_path) or project['path']
        # if repo_name.lower() == previous_repo_name:
        #     same_name_count += 1
        # else:
        #     if same_name_count > 1:
        #         print(f'{same_name_count} repositories with name {previous_repo_name}')
        #     previous_repo_name = repo_name.lower()
        #     same_name_count = 1
        github_repo_url = os.path.join(GITHUB_BASE_URL, github_org, f'{repo_name}.git')
        if not check_if_github_repo_exists(repo_name, github_org, github_token):
            gitlab_repo_url = os.path.join(gitlab_base_url, f'{repo_path}.git')
            migrate_repo(gitlab_repo_url, github_repo_url)
            migrated_project_count += 1
        else:
            print(f'{github_repo_url} already exists')
    print(f'{migrated_project_count} projects have been migrated, {len(gitlab_projects) - migrated_project_count} was already there.')


if __name__ == '__main__':
    args = sys.argv[1:]
    main(*args)
