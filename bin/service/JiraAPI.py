from bin.service import Environment
from bin.service import Logger
from bin.service import CardTransfer
from bin.service import RegEx
from bin.service import Storage
from atlassian import Jira
import time


class JiraAPI(Storage.Storage):

    def __init__(self):
        super().__init__()
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()
        self.jira = Jira(
            self.environment.get_endpoint_jira_host(),
            username=self.environment.get_endpoint_jira_user(),
            password=self.environment.get_endpoint_jira_password()
        )
        self.regex = RegEx.RegEx()
        self.card_transfer = CardTransfer.CardTransfer()

    def get_jira_keys(self):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        return list(jira_storage.distinct('key'))

    def get_jira_ids(self):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        return list(jira_storage.distinct('id'))

    def get_jira_card_ids(self):
        phoenix = self.mongo.phoenix
        card_storage = phoenix.card_storage
        return list(card_storage.distinct('relation_id', {'relation_type': 'jira'}))

    def sync_entries(self, wait=2):
        failed_jira_keys = []
        cached_total = 0

        leftover_jira_keys = self.get_jira_keys()
        projects = self.request_service_jira_projects()
        for project in projects:
            jira_keys = self.request_service_jira_keys(project)
            start = float(time.time())
            clean_cache = {}
            for jira_key in jira_keys:
                if jira_key in leftover_jira_keys:
                    leftover_jira_keys.remove(jira_key)
                else:
                    try:
                        clean_cache, failed_jira_keys = self.add_to_clean_cache(
                            jira_key,
                            failed_jira_keys,
                            clean_cache,
                            wait
                        )
                    except Exception as err:
                        self.logger.add_entry(self.__class__.__name__, str(err) + "; with Ticket " + jira_key)
            self.store_tickets(clean_cache)
            cached_current = len(clean_cache)
            cached_total += cached_current
            stop = float(time.time())
            seconds = (stop - start)
            print('>>> cached {} jira entries from project "{}" of {} entries total after {} seconds'.format(cached_current, project, cached_total, seconds))
            time.sleep(wait)
        self.transfer_entries()

    def transfer_entries(self):
        jira_ids = self.get_jira_ids()
        jira_card_ids = self.get_jira_card_ids()
        jira_ids_to_transfer = list(set(jira_ids) - set(jira_card_ids))
        print('>>> jira transfer started for {} cards'.format(len(jira_ids_to_transfer)))
        jira_entries = self.load_tickets(jira_ids_to_transfer)
        created_card_ids = self.card_transfer.transfer_jira(jira_entries)
        created_current = len(created_card_ids)
        print('>>> jira transfer successful, {} new cards created'.format(created_current))

    def entry_exists(self, jira_id):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        return jira_storage.find_one({'id': jira_id})

    def store_tickets(self, tickets):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        for jira_id in tickets:
            stored_ticket = jira_storage.find_one({'id': jira_id})
            if stored_ticket is not None:
                jira_storage.replace_one({'id': jira_id}, tickets[jira_id])
            else:
                jira_storage.insert_one(tickets[jira_id])

    def add_to_clean_cache(self, jira_key, failed_jira_keys, clean_cache, wait=2):
        ticket = None
        try:
            ticket_data = self.request_ticket_data(jira_key)
            ticket = {
                'id': ticket_data['id'],
                'key': jira_key,
                'title': ticket_data['fields']['summary'],
                'body': '',
                'created': ticket_data['fields']['created'],
                'updated': ticket_data['fields']['updated'],
                'keywords': ticket_data['fields']['labels'],
                'comments': [],
                'screenshot': self.get_screenshot(ticket_data)
            }
            if ticket_data['fields']['description'] is not None:
                ticket['body'] = self.regex.mask_text(ticket_data['fields']['description'])
            comments = ticket_data['fields']['comment']['comments']
            for comment in comments:
                if comment['body'] is not None:
                    ticket['comments'].append(self.regex.mask_text(comment['body']))
        except Exception as e:
            self.logger.add_entry(self.__class__.__name__, e)
            failed_jira_keys.append(jira_key)
        time.sleep(wait)
        if ticket is not None:
            clean_cache[str(ticket['id'])] = ticket
        return clean_cache, failed_jira_keys

    def get_screenshot(self, ticket_data):
        url = None
        if 'attachment' in ticket_data:
            for attachment in ticket_data['attachment']:
                if attachment['size'] > 4096 and self.regex.is_image(attachment['content']):
                    url = attachment['content']
                    break

        return url

    def load_cached_ticket(self, jira_id):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        return jira_storage.find_one({'id': jira_id})

    def load_tickets(self, jira_ids=None):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        if jira_ids is None:
            return jira_storage.find(no_cursor_timeout=True)
        else:
            return jira_storage.find({'id': {'$in': jira_ids}}, no_cursor_timeout=True)

    def request_ticket_data(self, jira_key):
        return self.jira.issue(jira_key)

    def request_service_jira_keys(self, project='SERVICE'):
        index = 0
        limit = 50
        all_keys = []
        while True:
            jql_request = f"project = {project} ORDER BY issuekey"
            result_keys = self.jira.jql(jql_request, ['key'], index, limit)
            if result_keys is None or len(result_keys['issues']) == 0:
                break
            for issue in result_keys['issues']:
                all_keys.append(issue['key'])
            index += limit
        return all_keys

    def request_service_jira_projects(self):
        projects = []

        raw_data = self.jira.projects()
        for project in raw_data:
            if project['key'] not in projects:
                projects.append(project['key'])

        return projects
