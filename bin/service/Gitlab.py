from bin.service import Environment
from bin.service import Logger
from pymongo import MongoClient
import urllib.request
import json
import time


class Gitlab:
    """Gitl API class"""

    def __init__(self):
        self.mongo = MongoClient()
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()

    def sync_commits(self):
        private_token = self.environment.get_endpoint_git_private_token()
        url = self.environment.get_endpoint_git_projects()
        commits = {}
        page = 0
        run = True
        while run:
            time.sleep(0.25)
            page += 1
            parsed_url = url.format(private_token, page)
            projects = self.git_request(parsed_url)
            if len(projects) > 0:
                for project in projects:
                    try:
                        project_commits = self.get_project_commits(project['id'])
                    except Exception as err:
                        self.logger.add_entry(self.__class__.__name__, str(err) + "; with space " + project['id'])
                        project_commits = []
                    for project_commit in project_commits:
                        commit = {
                            'id': project_commit['id'],
                            'title': project_commit['title'],
                            'body': project_commit['message'],
                            'created': project_commit['authored_date'],
                            'project': project['id']
                        }
                        commits[project_commit['id']] = commit
            else:
                run = False
        self.store_commits(commits)
        return self.load_cached_commits()

    def get_project_commits(self, project_id):
        private_token = self.environment.get_endpoint_git_private_token()
        url = self.environment.get_endpoint_git_commits()

        commits = []
        page = 0
        run = True
        while run:
            page += 1
            parsed_url = url.format(project_id, private_token, page)
            project_commits = self.git_request(parsed_url)
            if len(project_commits) > 0:
                for project_commit in project_commits:
                    commits.append(project_commit)
            else:
                run = False

        return commits

    @staticmethod
    def git_request(url):
        f = urllib.request.urlopen(url)
        json_raw = f.read().decode('utf-8')
        return json.loads(json_raw)

    def load_cached_commits(self):
        phoenix = self.mongo.phoenix
        gitlab_storage = phoenix.gitlab_storage
        return gitlab_storage.find()

    def store_commits(self, commits):
        phoenix = self.mongo.phoenix
        gitlab_storage = phoenix.gitlab_storage
        for commit_id in commits:
            stored_commit = gitlab_storage.find_one({'id': commit_id})
            if stored_commit is not None:
                gitlab_storage.replace_one({'id': commit_id}, commits[commit_id])
            else:
                gitlab_storage.insert_one(commits[commit_id])
