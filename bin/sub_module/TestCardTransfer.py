from bin.service import CardTransfer
import os


class TestCardTransfer:

    def __init__(self, jira_tickets, confluence_documents, test_path):
        self.test_path = test_path
        self.jira_tickets = jira_tickets
        self.confluence_documents = confluence_documents
        self.transfer = CardTransfer.CardTransfer(self.test_path)

    def run(self):

        is_existing = os.path.exists(self.test_path)
        if is_existing:
            os.remove(self.test_path)

        first_thirty_jira_keys = list(self.jira_tickets.keys())[:30]
        first_thirty_confluence_keys = list(self.confluence_documents.keys())[:30]

        jira_tickets = {}
        for jira_key in first_thirty_jira_keys:
            jira_tickets[jira_key] = self.jira_tickets[jira_key]

        confluence_documents = {}
        for confluence_id in first_thirty_confluence_keys:
            confluence_documents[confluence_id] = self.confluence_documents[confluence_id]

        expected_length = len(jira_tickets) + len(confluence_documents)
        created_ids = self.transfer.run(jira_tickets, confluence_documents)
        actual_length = len(created_ids)

        created_ids_after_update = self.transfer.run(jira_tickets, confluence_documents)
        update_length = len(created_ids_after_update)

        return expected_length == actual_length and update_length == 0
