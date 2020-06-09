from bin.service import Environment
from bin.service import JiraSignature
from bin.service import Logger
import oauth2 as oauth
from urllib import parse
import json
import os
import pickle
import time


class Jira:

    def __init__(self):
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()
        self.token = None
        self.consumer = None
        self.client = None
        self.init_api()

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

    def sync_entries(self):

        failed_jira_keys = []
        clean_cache = {}

        offset = 0
        max_results = 100

        jira_keys = self.request_service_jira_keys(offset, max_results)
        while len(jira_keys) > 0:
            for jira_id in jira_keys:
                jira_key = jira_keys[jira_id]
                try:
                    clean_cache, failed_jira_keys = self.add_to_clean_cache(
                        jira_key,
                        failed_jira_keys,
                        clean_cache,
                        jira_id
                    )
                except Exception as err:
                    self.logger.add_entry(self.__class__.__name__, str(err) + "; with Ticket " + jira_key)

            offset += max_results
            jira_keys = self.request_service_jira_keys(offset, max_results)

        self.update_cache_diff(clean_cache)

        return len(clean_cache)

    def update_cache_diff(self, clean_cache):
        old_cache = self.load_cached_tickets()
        for jira_id in old_cache:
            if jira_id not in clean_cache:
                clean_cache[jira_id] = old_cache[jira_id]
        cache_file = self.environment.get_path_jira_cache()
        file = open(cache_file, "wb")
        pickle.dump(clean_cache, file)

    def add_to_clean_cache(self, jira_key, failed_jira_keys, clean_cache, jira_id):
        ticket = None
        try:
            ticket_data = self.request_ticket_data(jira_key)
            ticket = {
                'title': ticket_data['fields']['summary'],
                'body': ticket_data['fields']['description'],
                'created': ticket_data['fields']['created'],
                'updated': ticket_data['fields']['updated'],
                'comments': []
            }
            comments = ticket_data['fields']['comment']['comments']
            for comment in comments:
                ticket['comments'].append(comment['body'])
        except Exception as e:
            self.logger.add_entry(self.__class__.__name__, e)
            failed_jira_keys.append(jira_key)
        time.sleep(0.5)
        if ticket is not None:
            clean_cache[str(jira_id)] = ticket
        return clean_cache, failed_jira_keys

    def load_cached_ticket(self, jira_id):
        ticket = None
        tickets = self.load_cached_tickets()
        if jira_id in tickets:
            ticket = tickets[jira_id]

        return ticket

    def load_cached_tickets(self):
        cache_file = self.environment.get_path_jira_cache()
        file_exists = os.path.exists(cache_file)
        if file_exists:
            file = open(cache_file, "rb")
            content = pickle.load(file)
        else:
            content = {}
        return content

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

    def request_service_jira_keys(self, offset=0, max_results=100):
        jira_keys = {}

        tickets_endpoint = self.environment.get_endpoint_tickets()
        data_url = tickets_endpoint.format(max_results, offset)
        response, content = self.client.request(data_url, "GET")
        if response['status'] != '200':
            raise Exception("Request failed with status code {}".format(response['status']))
        response_data = content.decode("utf-8")
        raw_data = json.loads(response_data)
        if 'issues' in raw_data:
            for issue in raw_data['issues']:
                jira_keys[issue['id']] = issue['key']

        return jira_keys

    def request_info(self):
        info_endpoint = self.environment.get_endpoint_info()
        response, content = self.client.request(info_endpoint, "GET")
        return response, content
