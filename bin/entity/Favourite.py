class Favourite:

    def __init__(self):
        self.id = None
        self.card_id = None
        self.created = None
        self.user_id = None
        self.card_title = None

    def __iter__(self):
        yield 'id', self.id
        yield 'card_id', self.card_id
        yield 'created', self.created
        yield 'user_id', self.user_id
        yield 'card_title', self.card_title
