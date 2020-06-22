class ShoutOut:

    def __init__(self):
        self.card_id = None
        self.user_id = None
        self.text = None
        self.created = None

    def __iter__(self):
        yield 'card_id', self.card_id
        yield 'user_id', self.user_id
        yield 'text', self.text
        yield 'created', self.created
