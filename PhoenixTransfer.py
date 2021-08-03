from bin.service import ConfluenceAPI
from bin.service import Gitlab
from bin.service import JiraAPI
from bin.service import Logger
from bin.service import Environment
import threading

logger = Logger.Logger()
environment = Environment.Environment()
try:

    confluence_done = False
    jira_done = False
    git_done = False

    def confluence_thread():
        global confluence_done
        print('--- confluence thread started ---')
        confluence = ConfluenceAPI.ConfluenceAPI()
        confluence.transfer_entries()
        confluence_done = True

    def jira_thread():
        global jira_done
        print('--- jira thread started ---')
        jira = JiraAPI.JiraAPI()
        jira.transfer_entries()
        jira_done = True

    def git_thread():
        global git_done
        print('--- git thread started ---')
        gitlab = Gitlab.Gitlab()
        gitlab.transfer_entries()
        git_done = True

    confluence_process = threading.Thread(target=confluence_thread)
    confluence_process.start()

    jira_process = threading.Thread(target=jira_thread)
    jira_process.start()

    if environment.get_service_enable_git():
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


except Exception as e:
    logger.add_entry('PhoenixSync', e)
