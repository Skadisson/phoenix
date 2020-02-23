from bin.entity import Card
from bin.service import CardStorage
from bin.service import Environment
import time
import copy
import datetime


class CardTransfer:

    def __init__(self, cache_path=None):
        self.jira_tickets = []
        self.confluence_entries = []
        self.storage = CardStorage.CardStorage(cache_path)
        self.environment = Environment.Environment()

    def run(self, jira_tickets=None, confluence_entries=None):
        created_jira_card_ids = self.transfer_jira(jira_tickets)
        created_confluence_card_ids = self.transfer_confluence(confluence_entries)

        return created_jira_card_ids + created_confluence_card_ids

    def transfer_jira(self, jira_tickets):
        created_jira_card_ids = []
        if jira_tickets is not None:
            for ticket_id in jira_tickets:
                jira_card = self.storage.get_jira_card(ticket_id)
                if jira_card is None:
                    card_id = self.storage.get_next_card_id()
                    jira_card = self.create_jira_card(ticket_id, jira_tickets[ticket_id], card_id)
                    self.storage.add_card(jira_card)
                    created_jira_card_ids.append(jira_card.id)
                elif jira_card.author is None:
                    self.update_jira_card(jira_tickets[ticket_id], jira_card)

        return created_jira_card_ids

    def transfer_confluence(self, confluence_entries):
        created_confluence_card_ids = []
        if confluence_entries is not None:
            for confluence_id in confluence_entries:
                confluence_card = self.storage.get_confluence_card(confluence_id)
                if confluence_card is None:
                    card_id = self.storage.get_next_card_id()
                    confluence_card = self.create_confluence_card(confluence_id, confluence_entries[confluence_id], card_id)
                    self.storage.add_card(confluence_card)
                    created_confluence_card_ids.append(confluence_card.id)
                elif confluence_card.author is None:
                    self.update_confluence_card(confluence_entries[confluence_id], confluence_card)

        return created_confluence_card_ids

    def create_jira_card(self, ticket_id, ticket, card_id):
        jira_card = Card.Card()
        jira_card.id = card_id
        jira_card.relation_id = ticket_id
        jira_card.relation_type = 'jira'
        jira_card.type = 'idea'
        jira_card.created = self.timestamp_from_ticket_time(ticket['Created'])
        jira_card.changed = self.timestamp_from_ticket_time(ticket['Updated'])
        jira_card.text = ''
        jira_card.external_link = 'https://jira.konmedia.com/browse/' + ticket['Key']
        if 'Text' in ticket and ticket['Text'] is not None:
            jira_card.text += ticket['Text']
        if 'Comments' in ticket and ticket['Comments'] is not None:
            jira_card.text += ' ' + ' '.join(ticket['Comments'])
        if 'Title' in ticket and ticket['Title'] is not None:
            jira_card.title = ticket['Title']
        if 'Keywords' in ticket and ticket['Keywords'] is not None:
            jira_card.keywords = ticket['Keywords']
        jira_card.versions = []

        return jira_card

    @staticmethod
    def timestamp_from_ticket_time(ticket_time):
        if ticket_time is None:
            return 0
        return time.mktime(datetime.datetime.strptime(ticket_time, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    @staticmethod
    def update_jira_card(ticket, jira_card):
        text_and_comments = ''
        if 'Text' in ticket and ticket['Text'] is not None:
            text_and_comments += ticket['Text']
        if 'Comments' in ticket and ticket['Comments'] is not None:
            text_and_comments += ' ' + ' '.join(ticket['Comments'])
        got_changes = (text_and_comments != ticket['Text']) \
                      or ('Title' in ticket and jira_card.title != ticket['Title']) \
                      or ('Keywords' in ticket and jira_card.keywords != ticket['Keywords'])
        if got_changes:
            jira_card.versions.append(jira_card)
            updated_jira_card = copy.deepcopy(jira_card)
            updated_jira_card.title = ticket['Title']
            updated_jira_card.text = ticket['Text']
            updated_jira_card.keywords = ticket['Keywords']
            updated_jira_card.changed = time.time()

    @staticmethod
    def create_confluence_card(confluence_id, confluence_entry, card_id):
        jira_card = Card.Card()
        jira_card.id = card_id
        jira_card.relation_id = confluence_id
        jira_card.relation_type = 'confluence'
        jira_card.type = 'idea'
        jira_card.created = 0
        jira_card.changed = 0
        jira_card.external_link = confluence_entry['link']
        if 'text' in confluence_entry and confluence_entry['text'] is not None:
            jira_card.text = confluence_entry['text']
        if 'title' in confluence_entry and confluence_entry['title'] is not None:
            jira_card.title = confluence_entry['title']
        jira_card.versions = []

        return jira_card

    @staticmethod
    def update_confluence_card(confluence_entry, confluence_card):
        got_changes = ('text' in confluence_entry and confluence_card.text != confluence_entry['text']) \
                      or ('title' in confluence_entry and confluence_card.title != confluence_entry['title'])
        if got_changes:
            confluence_card.versions.append(confluence_card)
            updated_jira_card = copy.deepcopy(confluence_card)
            updated_jira_card.title = confluence_entry['title']
            updated_jira_card.text = confluence_entry['text']
            updated_jira_card.changed = time.time()
