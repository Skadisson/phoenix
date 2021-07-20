from bin.service import Environment
from bin.service import JiraSignature
from bin.service import Logger
from bin.service import CardTransfer
from bin.service import RegEx
from bin.service import Storage
import oauth2 as oauth
from urllib import parse
import json
import os
import pickle
import time


class Jira(Storage.Storage):

    def __init__(self):
        super().__init__()
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()
        self.token = None
        self.consumer = None
        self.client = None
        self.regex = RegEx.RegEx()
        self.init_api()
        self.card_transfer = CardTransfer.CardTransfer()

    def init_api(self):
        self.init_consumer()
        self.init_client()

    def init_consumer(self):
        consumer_key = self.environment.get_endpoint_consumer_key()
        consumer_secret = self.environment.get_endpoint_consumer_secret()
        self.consumer = oauth.Consumer(consumer_key, consumer_secret)

    def init_client(self):
        tries = 3
        while self.token is None and tries > 0:
            self.retrieve_token()
            tries -= 1
        if self.token is None or tries == 0:
            raise Exception("Unable to retrieve sd api token, shutting down.")
        self.client = oauth.Client(self.consumer, self.token)
        self.client.set_signature_method(JiraSignature.JiraSignature())

    def sync_entries(self, wait=2):
        failed_jira_keys = []
        max_results = 100
        cached_total = 0

        projects = self.request_service_jira_projects()
        for project in projects:
            offset = 0
            jira_keys, total = self.request_service_jira_keys(offset, max_results, project)
            while len(jira_keys) > 0:
                start = float(time.time())
                clean_cache = {}
                for jira_id in jira_keys:
                    jira_key = jira_keys[jira_id]
                    try:
                        clean_cache, failed_jira_keys = self.add_to_clean_cache(
                            jira_key,
                            failed_jira_keys,
                            clean_cache,
                            jira_id,
                            wait
                        )
                    except Exception as err:
                        self.logger.add_entry(self.__class__.__name__, str(err) + "; with Ticket " + jira_key)
                self.store_tickets(clean_cache)
                cached_current = len(clean_cache)
                cached_total += cached_current
                stop = float(time.time())
                seconds = (stop - start)
                print('>>> cached {} jira entries of {} entries total in project "{}" after {} seconds'.format(cached_current, cached_total, project, seconds))
                time.sleep(wait)
                offset += max_results
                jira_keys, total = self.request_service_jira_keys(offset, max_results, project)
        self.transfer_entries()

    def transfer_entries(self):
        jira_entries = self.load_tickets()
        created_card_ids = self.card_transfer.transfer_jira(jira_entries)
        created_current = len(created_card_ids)
        self.card_transfer.close()
        print('>>> jira synchronization completed, {} new cards created'.format(created_current))

    def store_tickets(self, tickets):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        for jira_id in tickets:
            stored_ticket = jira_storage.find_one({'id': jira_id})
            if stored_ticket is not None:
                jira_storage.replace_one({'id': jira_id}, tickets[jira_id])
            else:
                jira_storage.insert_one(tickets[jira_id])

    def add_to_clean_cache(self, jira_key, failed_jira_keys, clean_cache, jira_id, wait=2):
        ticket = None
        try:
            ticket_data = self.request_ticket_data(jira_key)
            ticket = {
                'id': jira_id,
                'key': jira_key,
                'title': ticket_data['fields']['summary'],
                'body': '',
                'created': ticket_data['fields']['created'],
                'updated': ticket_data['fields']['updated'],
                'keywords': ticket_data['fields']['labels'],
                'comments': []
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
            clean_cache[str(jira_id)] = ticket
        return clean_cache, failed_jira_keys

    def load_cached_ticket(self, jira_id):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        return jira_storage.find_one({'id': jira_id})

    def load_tickets(self):
        phoenix = self.mongo.phoenix
        jira_storage = phoenix.jira_storage
        return jira_storage.find(no_cursor_timeout=True)

    def retrieve_token(self):
        self.token = self.load_token()
        if self.token is None or self.is_token_valid(self.token) is False:
            self.retrieve_token_url()

    def retrieve_token_url(self):
        request_token_url = self.environment.get_endpoint_request_token()
        self.client = oauth.Client(self.consumer)
        self.client.set_signature_method(JiraSignature.JiraSignature())
        resp, content = self.client.request(request_token_url, "POST")
        if resp['status'] != '200':
            raise Exception("Invalid response %s: %s" % (resp['status'],  content))
        request_token = dict(parse.parse_qsl(content))
        request_token_string = request_token[b'oauth_token'].decode("utf-8")
        request_secret_string = request_token[b'oauth_token_secret'].decode("utf-8")
        authorize_url = self.environment.get_endpoint_authorize()
        print("%s?oauth_token=%s" % (authorize_url, request_token_string))
        input('Please visit the URL and hit Enter')
        token = self.get_access_token(request_token_string, request_secret_string)
        token_is_valid = self.is_token_valid(token)
        if not token_is_valid:
            raise Exception("Right violation - shutting down")
        else:
            self.cache_token(token)
        self.token = token

    def get_access_token(self, request_token, request_secret):
        access_token_url = self.environment.get_endpoint_access_token()
        token = oauth.Token(request_token, request_secret)
        self.client = oauth.Client(self.consumer, token)
        self.client.set_signature_method(JiraSignature.JiraSignature())
        resp, content = self.client.request(access_token_url, "POST")
        access_token_response = dict(parse.parse_qsl(content))
        if b'oauth_problem' in access_token_response:
            access_problem = access_token_response[b'oauth_problem'].decode("utf-8")
            self.logger.add_entry(self.__class__.__name__, access_problem)
            raise Exception("No rights")
        access_token_final = access_token_response[b'oauth_token'].decode("utf-8")
        access_secret_final = access_token_response[b'oauth_token_secret'].decode("utf-8")
        access_token = oauth.Token(access_token_final, access_secret_final)
        return access_token

    def cache_token(self, token):
        token_path = self.environment.get_path_token()
        file = open(token_path, "wb")
        pickle.dump(obj=token, file=file)
        file.close()

    def load_token(self):

        token = None
        token_path = self.environment.get_path_token()
        file_exists = os.path.isfile(token_path)
        if file_exists:
            file = open(token_path, "rb")
            token = pickle.load(file)
            file.close()

        return token

    def is_token_valid(self, request_token_string):
        self.client = oauth.Client(self.consumer, request_token_string)
        self.client.set_signature_method(JiraSignature.JiraSignature())
        resp, content = self.request_info()
        if resp['status'] == '500':
            self.logger.add_entry(self.__class__.__name__, "Jira responded with status 500")
        return resp['status'] == '200'

    def request_ticket_data(self, jira_key):
        ticket_endpoint = self.environment.get_endpoint_ticket()
        data_url = ticket_endpoint.format(jira_key)
        response, content = self.client.request(data_url, "GET")
        if response['status'] != '200':
            raise Exception("Request failed with status code {}".format(response['status']))
        return json.loads(content.decode("utf-8"))

    def request_service_jira_keys(self, offset=0, max_results=100, project='SERVICE'):
        jira_keys = {}
        total = 0

        tickets_endpoint = self.environment.get_endpoint_tickets()
        data_url = tickets_endpoint.format(project, max_results, offset)
        response, content = self.client.request(data_url, "GET")
        if response['status'] != '200':
            raise Exception("Request failed with status code {}".format(response['status']))
        response_data = content.decode("utf-8")
        raw_data = json.loads(response_data)
        if 'issues' in raw_data:
            for issue in raw_data['issues']:
                jira_keys[issue['id']] = issue['key']
        if 'total' in raw_data:
            total = int(raw_data['total'])

        return jira_keys, total

    def request_service_jira_projects(self):
        projects = []

        projects_endpoint = self.environment.get_endpoint_projects()
        response, content = self.client.request(projects_endpoint, "GET")
        if response['status'] != '200':
            raise Exception("Request failed with status code {}".format(response['status']))
        response_data = content.decode("utf-8")
        raw_data = json.loads(response_data)
        for project in raw_data:
            if project['key'] not in projects:
                projects.append(project['key'])

        return projects

    def request_info(self):
        info_endpoint = self.environment.get_endpoint_info()
        response, content = self.client.request(info_endpoint, "GET")
        return response, content
