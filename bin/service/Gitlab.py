from bin.service import Environment
from bin.service import Logger
from bin.service import CardTransfer
from pymongo import MongoClient
import urllib.request
import json
import time


class Gitlab:

    def __init__(self):
        self.environment = Environment.Environment()
        self.mongo = MongoClient(self.environment.get_endpoint_mongo_db_cloud())
        self.logger = Logger.Logger()
        self.card_transfer = CardTransfer.CardTransfer()

    def sync_commits(self, wait=2):
        private_token = self.environment.get_endpoint_git_private_token()
        url = self.environment.get_endpoint_git_projects()
        cached_total = 0
        page = 0
        run = True
        while run:
            page += 1
            parsed_url = url.format(private_token, page)
            projects = self.git_request(parsed_url)
            if len(projects) > 0:
                for project in projects:
                    start = float(time.time())
                    commits = {}
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
                    self.store_commits(commits)
                    cached_current = len(commits)
                    cached_total += cached_current
                    stop = float(time.time())
                    seconds = (stop - start)
                    print('>>> cached {} gitlab entries of {} entries total after {} seconds'.format(cached_current, cached_total, seconds))
                    time.sleep(wait)
            else:
                run = False
        self.transfer_entries()

    def transfer_entries(self):
        cached_commits = self.load_cached_commits()
        created_card_ids = self.card_transfer.transfer_git(cached_commits)
        created_current = len(created_card_ids)
        print('>>> gitlab synchronization completed, {} new cards created'.format(created_current))

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
        return gitlab_storage.find(no_cursor_timeout=True)

    def store_commits(self, commits):
        phoenix = self.mongo.phoenix
        gitlab_storage = phoenix.gitlab_storage
        for commit_id in commits:
            stored_commit = gitlab_storage.find_one({'id': commit_id})
            if stored_commit is not None:
                gitlab_storage.replace_one({'id': commit_id}, commits[commit_id])
            else:
                gitlab_storage.insert_one(commits[commit_id])
