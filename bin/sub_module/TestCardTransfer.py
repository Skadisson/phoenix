from bin.service import CardTransfer
import os


class TestCardTransfer:

    def __init__(self, jira_tickets):
        self.test_path = 'src/card_test'
        self.jira_tickets = jira_tickets
        self.transfer = CardTransfer.CardTransfer(self.test_path)

    def run(self):
        os.remove(self.test_path)
        expected_length = len(self.jira_tickets)
        crated_ids = self.transfer.run(self.jira_tickets)
        actual_length = len(crated_ids)

        return expected_length == actual_length
