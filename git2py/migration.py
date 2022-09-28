from contextlib import contextmanager
import os
import re
import subprocess
from tkinter import N
import tempfile
import shutil
from gitlab import Gitlab
from github import Github, GithubException

GITHUB_BASE_URL = 'https://github.com'
GITHUB_API_BASE_URL = 'https://api.github.com'
DFLT_LOCAL_REPO_DIR = 'repo'


def run_cmd_line(exe, *args):
    return subprocess.check_output([exe] + list(args)).decode().strip()


def git(*args):
    return run_cmd_line('git', *args)


def npm(*args):
    return run_cmd_line('npm', *args)


@contextmanager
def cd(path):
   old_path = os.getcwd()
   os.chdir(path)
   try:
       yield
   finally:
       os.chdir(old_path)


def work_under_tmp_dir(func):
    def wrapper(*args, **kwargs):
        tmp_dir = tempfile.mkdtemp()
        with cd(tmp_dir):
            func(*args, **kwargs)
        shutil.rmtree(tmp_dir)
    return wrapper


@work_under_tmp_dir
def mirror_repo(gitlab_project, github_repo):
    gitlab_url = gitlab_project.http_url_to_repo
    github_url = github_repo.clone_url
    print(f'Mirroring repo from {gitlab_url} to {github_url} ...')
    git('clone', '--mirror', gitlab_url, '.')
    git('push', '--no-verify', '--mirror', github_url)
    print(f'Repo {github_url} has been mirrored successfully!')


def migrate_project(gitlab_project, github_repo_name, migrate_wikis):
    print(f'Migrating project data from "{gitlab_project.path_with_namespace}" to "{github_repo_name}" ...')
    if migrate_wikis:
        create_issues_from_wikis(gitlab_project)
    update_file('settings.ts', r'projectId: \d*', f'projectId: {gitlab_project.id}')
    update_file('settings.ts', r"repo: '.*'", f"repo: '{github_repo_name}'")
    npm('run', 'start')
    print(f'Project data have been migrated to {github_repo_name} successfully!')


def create_issues_from_wikis(gitlab_project):
    wikis = gitlab_project.wikis.list(get_all=True)
    issues = gitlab_project.issues.list(get_all=True)
    for wiki in reversed(wikis):
        issue_title = f'(migrated wiki) {wiki.slug}'
        if next((i for i in issues if i.title == issue_title), None) is None:
            wiki_content = gitlab_project.wikis.get(wiki.slug).content
            gitlab_project.issues.create(dict(
                title=issue_title,
                description=wiki_content,
            ))


def update_file(path, pattern, replace):
    with open(path, 'r+') as file:
        content = file.read()
        content_new = re.sub(pattern, replace, content, flags=re.M)
        # if content_new == content:
        #     raise RuntimeError(f'Failed to update file "{path}"!')
        file.seek(0)
        file.write(content_new)
        file.truncate()


class Migration:
    def __init__(
        self,
        gitlab_base_url,
        gitlab_token,
        github_token,
        github_org_name,
        node_gitlab_2_github_path,
        name_map=None,
        projects_to_ignore=None
    ):
        self._gitlab = Gitlab(url=gitlab_base_url, private_token=gitlab_token)
        github = Github(github_token)
        self._github_org = github.get_organization(github_org_name)
        self._node_gitlab_2_github_path = node_gitlab_2_github_path
        self._name_map = name_map or {}
        self._projects_to_ignore = projects_to_ignore or []

    def migrate(self, *, migrate_repositories=True, migrate_project_data=True, migrate_wikis=False):
        gitlab_projects = self._gitlab.projects.list(
            get_all=True,
            # page=10,
            order_by='name',
            sort='asc'
        )
        print(f'Starting migration of {len(gitlab_projects)} Gitlab projects to Github')
        with cd(self._node_gitlab_2_github_path):
            for gitlab_project in gitlab_projects:
                try:
                    self._migrate_project(gitlab_project, migrate_repositories, migrate_project_data, migrate_wikis)
                except Exception as e:
                    print(f'Failed migrating {gitlab_project.path_with_namespace}. Error message: {e}')

    def _migrate_project(self, gitlab_project, migrate_repositories, migrate_project_data, migrate_wikis):
        path_with_namespace = gitlab_project.path_with_namespace
        if path_with_namespace in self._projects_to_ignore:
            print(f'Skipping {path_with_namespace}')
        else:
            github_repo_name = self._name_map.get(gitlab_project.path_with_namespace) or gitlab_project.path
            if migrate_repositories:
                self._migrate_repo(gitlab_project, github_repo_name)
            if migrate_project_data:
                migrate_project(gitlab_project, github_repo_name, migrate_wikis)

    def _migrate_repo(self, gitlab_project, github_repo_name):
        try:
            github_repo = self._github_org.get_repo(github_repo_name)
        except GithubException as e:
            print(f'Creating repo {github_repo_name} on Github ...')
            github_repo = self._github_org.create_repo(
                name=github_repo_name,
                description=gitlab_project.description,
                private=True
            )
        try:
            github_repo.get_contents("/")
        except GithubException as e:
            if not gitlab_project.empty_repo:
                mirror_repo(gitlab_project, github_repo)

    __call__ = migrate


if __name__ == '__main__':    

    name_map = {
        'cavart/qc': 'qc-cavart',
        'everyone/dolu': 'dolu-everyone',
        'dkim/new_featurizer': 'new_featurizer-dkim',
        'owenlloyd/ocore': 'ocore-owenlloyd',
        'dkim/ocore': 'ocore-dkim',
        'owenlloyd/omodel': 'omodel-owenlloyd',
        'dkim/omodel': 'omodel-dkim',
        'dkim/omodel_runners': 'omodel_runners-dkim',
        'dkim/otosentio_utils': 'otosentio_utils-dkim',
        'vmacari/sentio': 'sentio-vmacari',
        'Raka.Singh/sentio': 'sentio-Raka.Singh',
        'bernal/sentio': 'sentio-bernal',
        'sherzog/stroll': 'stroll-sherzog',
    }

    projects_to_ignore = [
        'zfeng2/raspbian_sentio_images',
        'isaac_rhett/c_can_decoder'
    ]

    migration = Migration(
        gitlab_base_url='https://git.otosense.ai/',
        gitlab_token='-xW-G5-2uTM2d7qZxnJ2',
        github_token='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',
        github_org_name='otosense',
        node_gitlab_2_github_path='/Users/vferon/otosense/migrate_from_gitlab_to_github/node-gitlab-2-github',
        name_map=name_map,
        projects_to_ignore=projects_to_ignore
    )

    migration(migrate_wikis=True)
