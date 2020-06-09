from bin.service import Environment
import urllib.request
import json
import time
import os
import pickle


class Gitlab:
    """Gitl API class"""

    def __init__(self):
        self.environment = Environment.Environment()

    def sync_commits(self):

        private_token = self.environment.get_endpoint_git_private_token()
        url = self.environment.get_endpoint_git_projects()

        commits = self.load_cached_commits()
        new_commits = 0
        page = 0
        run = True
        while run:
            time.sleep(0.25)
            page += 1
            parsed_url = url.format(private_token, page)
            projects = self.git_request(parsed_url)
            if len(projects) > 0:
                for project in projects:
                    project_commits = self.get_project_commits(project['id'])
                    for project_commit in project_commits:
                        if project_commit['id'] not in commits:
                            new_commits += 1
                            commit = {
                                'title': project_commit['title'],
                                'text': project_commit['message'],
                                'date': project_commit['authored_date'],
                                'project': project['id']
                            }
                            commits[project_commit['id']] = commit
            else:
                run = False

        self.store_commits(commits)
        return len(commits), new_commits

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

        confluence_commits = {}
        git_cache_path = self.environment.get_path_git_cache()
        file_exists = os.path.isfile(git_cache_path)
        if file_exists:
            file = open(git_cache_path, "rb")
            confluence_commits = pickle.load(file)
            file.close()

        return confluence_commits

    def store_commits(self, commits):

        git_cache_path = self.environment.get_path_git_cache()
        file = open(git_cache_path, "wb")
        pickle.dump(obj=commits, file=file)
        file.close()
