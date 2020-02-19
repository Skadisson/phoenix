from bin.service import Relevancy


class TestRelevancy:

    def __init__(self, test_data):
        self.test_data = test_data
        self.relevancy = Relevancy.Relevancy()
        self.test_keywords = {
            'Test One': 'Sebastian Philipp Claudia',
            'Test Two': 'bb32 print template'
        }

    def run(self):

        result_one = self.relevancy.assertain_tickets(self.test_keywords['Test One'].split(), self.test_data)
        print(result_one)

        result_two = self.relevancy.assertain_tickets(self.test_keywords['Test Two'].split(), self.test_data)
        print(result_two)

        return True
