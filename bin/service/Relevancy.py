from bin.service import SciKitLearn
import collections


class Relevancy:

    def __init__(self):
        self.scikit = SciKitLearn.SciKitLearn()

    def assertain_tickets(self, search, tickets):
        result = {}

        ticket_items = []
        for jira_id in tickets:
            ticket = tickets[jira_id]
            ticket_words = collections.Counter()
            if 'Keywords' in ticket and ticket['Keywords'] is not None:
                ticket_words.update(ticket['Keywords'])
            if 'Comments' in ticket and ticket['Comments'] is not None:
                ticket_words.update(ticket['Comments'])
            ticket_items.append({
                'jira_id': jira_id,
                'words': ticket_words.keys()
            })

        relevancy = self.scikit.assertain(['words'], ticket_items, ['jira_id'], search)
        print(relevancy)
        exit()

        return result
