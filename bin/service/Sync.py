from bin.service import ConfluenceAPI
from bin.service import Gitlab
from bin.service import JiraAPI
from bin.service import Logger
from bin.service import Environment
from bin.service import SciKitLearn
import threading
import yaml
import os

confluence_done = False
jira_done = False
git_done = False
sync = None


class Sync:

    def __init__(self):
        self.logger = Logger.Logger()
        self.environment = Environment.Environment()

    def run(self):

        if self.is_running():
            return
        self.store_yaml({'running': True, 'current': 0, 'total': 0})

        global confluence_done, jira_done, git_done, sync
        sync = self

        try:

            def confluence_thread():
                global confluence_done, sync
                print('--- confluence thread started ---')
                confluence = ConfluenceAPI.ConfluenceAPI()
                confluence.sync_entries(0, sync)
                confluence_done = True

            def jira_thread():
                global jira_done, sync
                print('--- jira thread started ---')
                jira = JiraAPI.JiraAPI()
                jira.sync_entries(0, sync)
                jira_done = True

            def git_thread():
                global git_done, sync
                print('--- git thread started ---')
                gitlab = Gitlab.Gitlab()
                gitlab.sync_commits(0, sync)
                git_done = True

            confluence_process = threading.Thread(target=confluence_thread)
            confluence_process.start()

            jira_process = threading.Thread(target=jira_thread)
            jira_process.start()

            if self.environment.get_service_enable_git():
                git_process = threading.Thread(target=git_thread)
                git_process.start()
                while False in [confluence_done, jira_done, git_done]:
                    pass
                confluence_process.join()
                jira_process.join()
                git_process.join()
            else:
                while False in [confluence_done, jira_done]:
                    pass
                confluence_process.join()
                jira_process.join()

            print('--- training started ---')
            scikit = SciKitLearn.SciKitLearn()
            scikit.train()

            self.set_running(False)

        except Exception as e:
            print(e)
            self.logger.add_entry('PhoenixSync', e)
            self.set_running(False)

    def set_running(self, running=True):
        state = self.load_yaml()
        state['running'] = running
        self.store_yaml(state)

    def add_total(self, total=1):
        state = self.load_yaml()
        state['total'] += total
        self.store_yaml(state)

    def add_current(self, current=1):
        state = self.load_yaml()
        state['current'] += current
        self.store_yaml(state)

    def is_running(self):
        state = self.load_yaml()
        return state['running']

    def load_yaml(self):
        sync_path = self.environment.get_path_sync_state()
        data = None
        if os.path.exists(sync_path):
            file = open(sync_path, "r", encoding='utf8')
            data = yaml.load(file, Loader=yaml.FullLoader)

        if data is None:
            data = {'running': False, 'current': 0, 'total': 0}

        return data

    def store_yaml(self, data):
        if data is None:
            data = {'running': False, 'current': 0, 'total': 0}
        sync_path = self.environment.get_path_sync_state()
        file = open(sync_path, "w", encoding='utf8')
        yaml.dump(data, file, Dumper=yaml.Dumper)
