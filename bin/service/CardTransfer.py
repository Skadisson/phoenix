from bin.entity import Card
from bin.service import CardStorage
from bin.service import Environment
import time
import copy


class CardTransfer:

    def __init__(self, cache_path=None):
        self.jira_tickets = []
        self.confluence_entries = []
        self.storage = CardStorage.CardStorage(cache_path)
        self.environment = Environment.Environment()

    def run(self, jira_tickets=None, confluence_entries=None):
        created_jira_card_ids = self.transfer_jira(jira_tickets)

        return created_jira_card_ids

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

    @staticmethod
    def create_jira_card(ticket_id, ticket, card_id):
        jira_card = Card.Card()
        jira_card.id = card_id
        jira_card.relation_id = ticket_id
        jira_card.relation_type = 'jira'
        jira_card.type = 'idea'
        jira_card.created = time.time()
        jira_card.changed = time.time()
        jira_card.text = ticket['Text']
        jira_card.title = ticket['Title']
        jira_card.keywords = ticket['Keywords']
        jira_card.versions = []

        return jira_card

    @staticmethod
    def update_jira_card(ticket, jira_card):
        got_changes = jira_card.text != ticket['Text'] or jira_card.title != ticket['Title'] or jira_card.keywords != ticket['Keywords']
        if got_changes:
            jira_card.versions.append(jira_card)
            updated_jira_card = copy.deepcopy(jira_card)
            updated_jira_card.title = ticket['Title']
            updated_jira_card.text = ticket['Text']
            updated_jira_card.keywords = ticket['Keywords']
            updated_jira_card.changed = time.time()
