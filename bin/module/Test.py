from bin.sub_module import TestCardTransfer, TestInfo, TestOwnership, TestContextSearch
from bin.service import Environment
from bin.service import Logger
import os
import pickle


class Test:

    def __init__(self):
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()
        self.test_path = 'tmp/card_test'

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:
            jira_test_data = self.load_jira_test_data()
            confluence_test_data = self.load_confluence_test_data()

            success = True
            if success:
                success = self.test_card_transfer(jira_test_data, confluence_test_data)
                result['items'].append({
                    'test': 'CardTransfer',
                    'success': success
                })

            if success:
                success = self.test_ownership()
                result['items'].append({
                    'test': 'Ownership',
                    'success': success
                })

            if success:
                success = self.test_info(1)
                result['items'].append({
                    'test': 'Info',
                    'success': success
                })

            if success:
                success = self.test_context_search()
                result['items'].append({
                    'test': 'ContextSearch',
                    'success': success
                })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result

    def load_jira_test_data(self):
        test_data = None
        test_data_path = self.environment.get_path_jira_test_data()
        file_exists = os.path.isfile(test_data_path)
        if file_exists:
            file = open(test_data_path, "rb")
            test_data = pickle.load(file)
            file.close()
        return test_data

    def load_confluence_test_data(self):
        test_data = None
        test_data_path = self.environment.get_path_confluence_test_data()
        file_exists = os.path.isfile(test_data_path)
        if file_exists:
            file = open(test_data_path, "rb")
            test_data = pickle.load(file)
            file.close()
        return test_data

    def test_card_transfer(self, jira_test_data, confluence_test_data):
        test_transfer = TestCardTransfer.TestCardTransfer(jira_test_data, confluence_test_data, self.test_path)
        result = test_transfer.run()
        return result

    def test_ownership(self):
        test_ownership = TestOwnership.TestOwnership(self.test_path)
        result = test_ownership.run()
        return result

    def test_info(self, owned_count):
        test_info = TestInfo.TestInfo(self.test_path, owned_count)
        result = test_info.run()
        return result

    def test_context_search(self):
        test_context_search = TestContextSearch.TestContextSearch(self.test_path)
        result = test_context_search.run()
        return result
