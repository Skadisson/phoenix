from bin.service import Logger, CardTransfer, Confluence, Jira


class Update:

    def __init__(self):
        self.logger = Logger.Logger()
        self.card_transfer = CardTransfer.CardTransfer()
        self.jira = Jira.Jira()
        self.confluence = Confluence.Confluence()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }

        try:

            tickets = self.jira.load_tickets()
            confluence_entries = self.confluence.load_entries()
            created_ids = self.card_transfer.run(tickets, confluence_entries)
            result['items'].append({
                'created_ids': created_ids
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
