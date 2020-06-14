from bin.service import ConfluenceAPI
from bin.service import Gitlab
from bin.service import Jira
from bin.service import Logger
from bin.service import CardTransfer
import time
import _thread

delay_in_seconds = 60 * 5
items_per_run = 100
prefer_new = True

logger = Logger.Logger()
try:

    start_total = float(time.time())

    start = float(time.time())
    confluence = ConfluenceAPI.ConfluenceAPI()
    confluence_entries = confluence.sync_entries()
    stop = float(time.time())
    minutes = (stop - start) / 60
    print('--- confluence entries synced after {} minutes ---'.format(minutes))

    """start = float(time.time())
    jira = Jira.Jira()
    jira_entries = jira.sync_entries()
    stop = float(time.time())
    minutes = (stop - start) / 60
    print('--- jira tickets synced after {} minutes ---'.format(minutes))"""

    """start = float(time.time())
    gitlab = Gitlab.Gitlab()
    git_entries = gitlab.sync_commits()
    stop = float(time.time())
    minutes = (stop - start) / 60
    print('--- git commits synced after {} minutes ---'.format(minutes))"""
    jira_entries = None
    git_entries = None

    start = float(time.time())
    transfer = CardTransfer.CardTransfer()
    transfer.run(jira_entries, confluence_entries, git_entries)
    stop = float(time.time())
    minutes = (stop - start) / 60
    print('--- cards created and updated after {} minutes ---'.format(minutes))

    stop_total = float(time.time())
    minutes_total = (stop_total - start_total) / 60

    completed_message = '--- sync completed after {} minutes ---'.format(minutes_total)
    print(completed_message)
    logger.add_entry('PhoenixSync', completed_message)

except Exception as e:
    logger.add_entry('PhoenixSync', e)
