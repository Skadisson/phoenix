from bin.service import ConfluenceAPI
from bin.service import Gitlab
from bin.service import Jira
from bin.service import Logger
from bin.service import CardStorage
import time

logger = Logger.Logger()
try:

    storage = CardStorage.CardStorage()
    storage.backup()

    start_total = float(time.time())

    start = float(time.time())
    confluence = ConfluenceAPI.ConfluenceAPI()
    confluence_count = confluence.sync_entries()
    stop = float(time.time())
    minutes = (stop - start) / 60
    print('--- {} confluence entries synced after {} minutes ---'.format(confluence_count, minutes))

    start = float(time.time())
    jira = Jira.Jira()
    jira_count = jira.sync_entries()
    stop = float(time.time())
    minutes = (stop - start) / 60
    print('--- {} jira tickets synced after {} minutes ---'.format(jira_count, minutes))

    start = float(time.time())
    gitlab = Gitlab.Gitlab()
    gitlab_count, new_commits = gitlab.sync_commits()
    stop = float(time.time())
    minutes = (stop - start) / 60
    print('--- {} git commits, including {} new commits, synced after {} minutes ---'.format(gitlab_count, new_commits, minutes))

    stop_total = float(time.time())
    minutes_total = (stop_total - start_total) / 60

    completed_message = '--- sync completed after {} minutes ---'.format(minutes_total)
    print(completed_message)
    logger.add_entry('PhoenixSync', completed_message)

except Exception as e:
    logger.add_entry('PhoenixSync', e)
