from bin.service import ConfluenceAPI
from bin.service import Gitlab
from bin.service import JiraAPI
from bin.service import Logger
from bin.service import Environment
from bin.service import SciKitLearn
import threading
import yaml
import os
import time
import numpy

confluence_done = False
jira_done = False
git_done = False


class Sync:

    def __init__(self):
        self.logger = Logger.Logger()
        self.environment = Environment.Environment()

    def run(self, override=False):

        if self.is_running() and override is False:
            return
        self.set_running(True)
        self.set_last(time.time())
        start = time.time()

        global confluence_done, jira_done, git_done

        try:

            def confluence_thread():
                global confluence_done
                print('--- confluence thread started ---')
                confluence = ConfluenceAPI.ConfluenceAPI()
                confluence.sync_entries(0)
                confluence_done = True

            def jira_thread():
                global jira_done
                print('--- jira thread started ---')
                jira = JiraAPI.JiraAPI()
                jira.sync_entries(0)
                jira_done = True

            def git_thread():
                global git_done
                print('--- git thread started ---')
                gitlab = Gitlab.Gitlab()
                gitlab.sync_commits(0)
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

            end = time.time()
            self.add_runtime((end-start))
            self.set_running(False)

        except Exception as e:
            print(e)
            self.logger.add_entry('PhoenixSync', e)
            self.set_running(False)

    def set_running(self, running=True):
        state = self.load_yaml()
        if state is not None:
            state['running'] = running
            self.store_yaml(state)

    def set_last(self, last):
        state = self.load_yaml()
        if state is not None:
            state['last'] = last
            self.store_yaml(state)

    def add_runtime(self, runtime):
        state = self.load_yaml()
        if state is not None:
            state['runtimes'].append(runtime)
            state['average'] = float(numpy.average(state['runtimes']))
            self.store_yaml(state)

    def is_running(self):
        state = self.load_yaml()
        runs = True
        if state is not None:
            is_running = state['running']
            half_a_day = 60 * 60 * 12
            got_time = state['last'] != 0
            is_in_range = time.time() - state['last'] <= half_a_day
            runs = is_running or (got_time and is_in_range)

        return runs

    def load_yaml(self):
        sync_path = self.environment.get_path_sync_state()
        data = None
        if os.path.exists(sync_path):
            file = open(sync_path, "r", encoding='utf8')
            data = yaml.load(file, Loader=yaml.FullLoader)
        if data is None:
            data = {'last': time.time(), 'average': 0, 'runtimes': [], 'running': False}

        return data

    def store_yaml(self, data):
        if data is None:
            data = {'last': time.time(), 'average': 0, 'runtimes': [], 'running': False}
        sync_path = self.environment.get_path_sync_state()
        file = open(sync_path, "w", encoding='utf8')
        yaml.dump(data, file, Dumper=yaml.Dumper)
