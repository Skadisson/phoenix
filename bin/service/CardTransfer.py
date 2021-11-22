from bin.entity import Card
from bin.service import CardStorage, NormalCache
import time
import copy
import datetime


class CardTransfer:

    def __init__(self):
        self.storage = CardStorage.CardStorage()
        self.normal_cache = NormalCache.NormalCache()

    def transfer_jira(self, jira_tickets):
        start = time.time()
        created_jira_card_ids = []
        if jira_tickets is not None:
            total = jira_tickets.count()
            step = round(total/10)
            current = 0
            for ticket in jira_tickets:
                current += 1
                jira_card = self.storage.get_jira_card(ticket['id'])
                if jira_card is None:
                    card_id = self.storage.get_next_card_id()
                    jira_card = self.create_jira_card(ticket['id'], ticket, card_id)
                    self.storage.add_card(jira_card)
                    created_jira_card_ids.append(jira_card['id'])
                elif jira_card['author'] is None:
                    jira_card = self.update_jira_card(ticket['id'], jira_card)
                    self.storage.update_card(jira_card)
                if jira_card is not None:
                    self.normal_cache.normalize_card(jira_card)
                now = time.time()
                if step > 0 and current % step == 0:
                    percentage = round((current / total) * 100)
                    minutes = round((now - start) / 60, ndigits=2)
                    print('>>> transfered {} % of jira entries after {} minutes ({}/{})'.format(percentage, minutes, current, total))

        return created_jira_card_ids

    def transfer_confluence(self, confluence_entries):
        start = time.time()
        created_confluence_card_ids = []
        if confluence_entries is not None:
            total = confluence_entries.count()
            step = round(total/10)
            current = 0
            for confluence_entry in confluence_entries:
                current += 1
                confluence_card = self.storage.get_confluence_card(confluence_entry['id'])
                if confluence_card is None:
                    card_id = self.storage.get_next_card_id()
                    confluence_card = self.create_confluence_card(confluence_entry['id'], confluence_entry, card_id)
                    self.storage.add_card(confluence_card)
                    created_confluence_card_ids.append(confluence_card['id'])
                elif confluence_card['author'] is None:
                    self.update_confluence_card(confluence_entry, confluence_card)
                    self.storage.update_card(confluence_card)
                if confluence_card is not None:
                    self.normal_cache.normalize_card(confluence_card)
                now = time.time()
                if step == 0 or current % step == 0:
                    percentage = round((current / total) * 100)
                    minutes = round((now - start) / 60, ndigits=2)
                    print('>>> transfered {} % of confluence entries after {} minutes ({}/{})'.format(percentage, minutes, current, total))

        return created_confluence_card_ids

    def transfer_git(self, git_entries):
        start = time.time()
        created_git_card_ids = []
        if git_entries is not None:
            total = git_entries.count()
            step = round(total/10)
            current = 0
            for git_entry in git_entries:
                current += 1
                git_card = self.storage.get_git_card(git_entry['id'])
                if git_card is None:
                    card_id = self.storage.get_next_card_id()
                    git_card = self.create_git_card(git_entry['id'], git_entry, card_id)
                    self.storage.add_card(git_card)
                    created_git_card_ids.append(git_card['id'])
                elif git_card['author'] is None:
                    self.update_git_card(git_entry['id'], git_card)
                    self.storage.update_card(git_card)
                if git_card is not None:
                    self.normal_cache.normalize_card(git_card)
                now = time.time()
                if current % step == 0:
                    percentage = round((current / total) * 100)
                    minutes = round((now - start) / 60, ndigits=2)
                    print('>>> transfered {} % of git entries after {} minutes ({}/{})'.format(percentage, minutes, current, total))

        return created_git_card_ids

    def create_jira_card(self, ticket_id, ticket, card_id):
        jira_card = Card.Card()
        jira_card.id = card_id
        jira_card.relation_id = ticket_id
        jira_card.relation_type = 'jira'
        jira_card.type = 'idea'
        jira_card.created = self.timestamp_from_atlassian_time(ticket['created'])
        jira_card.changed = self.timestamp_from_atlassian_time(ticket['updated'])
        jira_card.text = ''
        jira_card.external_link = ''
        jira_card.screenshot = ''
        if 'key' in ticket and ticket['key'] is not None:
            jira_card.external_link = 'https://jira.konmedia.com/browse/' + ticket['key']
        if 'title' in ticket and ticket['title'] is not None:
            jira_card.title = ticket['title']
        if 'organization' in ticket and ticket['organization'] is not None and ticket['organization'] != '':
            if ticket['organization'] is list:
                organization = ' '.join(ticket['organization']) + ' '
            else:
                organization = ticket['organization'] + ' '
            jira_card.text += str(organization)
        if 'body' in ticket and ticket['body'] is not None:
            jira_card.text += ticket['body']
        if 'comments' in ticket and ticket['comments'] is list:
            jira_card.text += ' ' + ' '.join(ticket['comments'])
        if 'keywords' in ticket and ticket['keywords'] is list:
            jira_card.keywords = ticket['keywords']
        if 'screenshot' in ticket and ticket['screenshot'] != '':
            jira_card.screenshot = ticket['screenshot']

        return dict(jira_card)

    @staticmethod
    def timestamp_from_atlassian_time(ticket_time):
        if ticket_time is None:
            return 0
        return time.mktime(datetime.datetime.strptime(ticket_time, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    @staticmethod
    def update_jira_card(ticket, jira_card):
        text_and_comments = ''
        if 'body' in ticket and ticket['body'] is not None:
            text_and_comments += ticket['body']
        if 'comments' in ticket and ticket['comments'] is list:
            text_and_comments += ' ' + ' '.join(ticket['comments'])
        got_changes = (text_and_comments != jira_card['text']) \
                      or ('title' in ticket and jira_card['title'] != ticket['title']) \
                      or ('keywords' in ticket and jira_card['keywords'] != ticket['keywords'])
        if got_changes:
            updated_jira_card = copy.deepcopy(jira_card)
            if 'title' in ticket and ticket['title'] is not None:
                updated_jira_card['title'] = ticket['title']
            if 'body' in ticket and ticket['body'] is not None:
                updated_jira_card['text'] = ticket['body']
            if 'keywords' in ticket and ticket['keywords'] is not None:
                updated_jira_card['keywords'] = ticket['keywords']
            updated_jira_card['changed'] = time.time()
            jira_card = updated_jira_card
        return jira_card

    def create_confluence_card(self, confluence_id, confluence_entry, card_id):
        confluence_card = Card.Card()
        confluence_card.id = card_id
        confluence_card.relation_id = confluence_id
        confluence_card.relation_type = 'confluence'
        confluence_card.type = 'idea'
        confluence_card.created = self.timestamp_from_confluence_time(confluence_entry['created'])
        confluence_card.changed = self.timestamp_from_confluence_time(confluence_entry['created'])
        confluence_card.external_link = confluence_entry['link']
        if 'body' in confluence_entry and confluence_entry['body'] is not None:
            confluence_card.text = confluence_entry['body']
        if 'title' in confluence_entry and confluence_entry['title'] is not None:
            confluence_card.title = confluence_entry['title']

        return dict(confluence_card)

    @staticmethod
    def update_git_card(git_entry, git_card):
        got_changes = ('body' in git_entry and git_card['text'] != git_entry['body']) \
                      or ('title' in git_entry and git_card['title'] != git_entry['title'])
        if got_changes:
            updated_git_card = copy.deepcopy(git_card)
            if 'title' in git_card and git_card['title'] is not None:
                updated_git_card['title'] = git_card['title']
            if 'body' in git_card and git_card['body'] is not None:
                updated_git_card['text'] = git_card['body']
            updated_git_card['changed'] = time.time()

    def create_git_card(self, git_id, git_entry, card_id):
        git_card = Card.Card()
        git_card.id = card_id
        git_card.relation_id = git_id
        git_card.relation_type = 'git'
        git_card.type = 'idea'
        if 'created' in git_entry and git_entry['created'] is not None:
            git_card.created = self.timestamp_from_confluence_time(git_entry['created'])
            git_card.changed = self.timestamp_from_confluence_time(git_entry['created'])
        git_card.external_link = ''
        if 'body' in git_entry and git_entry['body'] is not None:
            git_card.text = git_entry['body']
        if 'title' in git_entry and git_entry['title'] is not None:
            git_card.title = git_entry['title']

        return dict(git_card)

    @staticmethod
    def timestamp_from_confluence_time(confluence_time):
        if confluence_time is None:
            return 0
        return time.mktime(datetime.datetime.strptime(confluence_time, "%Y-%m-%dT%H:%M:%S.%f%z").timetuple())

    def update_confluence_card(self, confluence_entry, confluence_card):
        got_changes = ('body' in confluence_entry and confluence_card['text'] != confluence_entry['body']) \
                      or ('title' in confluence_entry and confluence_card['title'] != confluence_entry['title'])
        if got_changes:
            updated_confluence_card = copy.deepcopy(confluence_card)
            if 'title' in confluence_entry and confluence_entry['title'] is not None:
                updated_confluence_card['title'] = confluence_entry['title']
            if 'body' in confluence_entry and confluence_entry['body'] is not None:
                updated_confluence_card['text'] = confluence_entry['body']
            updated_confluence_card['changed'] = time.time()
            if updated_confluence_card['created'] is None:
                updated_confluence_card['created'] = self.timestamp_from_atlassian_time(confluence_entry['created'])
            updated_confluence_card['changed'] = self.timestamp_from_atlassian_time(confluence_entry['created'])
