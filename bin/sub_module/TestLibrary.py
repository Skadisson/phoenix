from bin.service import Library


class TestLibrary:

    def __init__(self, test_data):
        self.test_data = test_data
        self.library = Library.Library()
        self.expected_length = 53308
        self.expected_index = 22

    def run(self):
        self.library.add_tickets(self.test_data)
        actual_length = len(self.library.get_words())
        if actual_length != self.expected_length:
            raise Exception("Library failed to accumulate test words ({} != {})".format(actual_length, self.expected_length))
        actual_index = self.library.get_index('Sebastian')
        if actual_index != 22:
            raise Exception("Library failed to locate test word ({} != {})".format(actual_index, self.expected_index))
        return True
