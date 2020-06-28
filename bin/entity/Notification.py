class Notification:

    def __init__(self):
        self.card_id = None
        self.is_shout_out = None
        self.title = None
        self.user_id = None
        self.created = None
        self.notified = None

    def __iter__(self):
        yield 'card_id', self.card_id
        yield 'is_shout_out', self.is_shout_out
        yield 'title', self.title
        yield 'user_id', self.user_id
        yield 'created', self.created
        yield 'notified', self.notified
