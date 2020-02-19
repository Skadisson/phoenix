from bin.sub_module import TestLibrary, TestRelevancy
from bin.service import Environment
from bin.service import Logger
import os, pickle


class Test:

    def __init__(self):
        self.environment = Environment.Environment()
        self.logger = Logger.Logger()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:
            test_data = self.load_test_data()

            success = self.test_library(test_data)
            result['items'].append({
                'test': 'Library',
                'success': success
            })

            success = self.test_relevancy(test_data)
            result['items'].append({
                'test': 'Relevancy',
                'success': success
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result

    def load_test_data(self):
        test_data = None
        test_data_path = self.environment.get_path_test_data()
        file_exists = os.path.isfile(test_data_path)
        if file_exists:
            file = open(test_data_path, "rb")
            test_data = pickle.load(file)
            file.close()
        return test_data

    def test_library(self, test_data):
        test_library = TestLibrary.TestLibrary(test_data)
        result = test_library.run()
        return result

    def test_relevancy(self, test_data):
        test_relevancy = TestRelevancy.TestRelevancy(test_data)
        result = test_relevancy.run()
        return result
