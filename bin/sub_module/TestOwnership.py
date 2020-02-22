from bin.service import CardStorage


class TestOwnership:

    def __init__(self, test_path):
        self.test_path = test_path
        self.card_id = 10
        self.card_storage = CardStorage.CardStorage(self.test_path)

    def run(self):

        expected_card_exists = True
        actual_card_exists = self.card_storage.card_exists(self.card_id)
        success = expected_card_exists == actual_card_exists

        if success:
            self.card_storage.update_editors(self.card_id, 'ses')
            card_after_update = self.card_storage.get_card(self.card_id)
            success = card_after_update.author == 'ses' and len(card_after_update.editors) == 1

        return success
