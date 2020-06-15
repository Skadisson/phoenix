from bin.service import ConfluenceAPI
from bin.service import Gitlab
from bin.service import Jira
from bin.service import Logger
import _thread
import threading

logger = Logger.Logger()
try:

    def confluence_thread():
        print('--- confluence thread started ---')
        confluence = ConfluenceAPI.ConfluenceAPI()
        confluence.sync_entries(0)

    _thread.start_new_thread(confluence_thread, ())

    def jira_thread():
        print('--- jira thread started ---')
        jira = Jira.Jira()
        jira.sync_entries(0)

    _thread.start_new_thread(jira_thread, ())

    def git_thread():
        print('--- git thread started ---')
        gitlab = Gitlab.Gitlab()
        gitlab.sync_commits(0)

    """_thread.start_new_thread(git_thread, ())"""

    while threading.activeCount():
        pass

except Exception as e:
    logger.add_entry('PhoenixSync', e)
