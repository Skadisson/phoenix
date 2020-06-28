class Query:

    def __init__(self):
        self.card_id = None
        self.query = None
        self.searched = None
        self.loading_seconds = None
        self.frontend = None

    def __iter__(self):
        yield 'card_id', self.card_id
        yield 'query', self.query
        yield 'searched', self.searched
        yield 'loading_seconds', self.loading_seconds
        yield 'frontend', self.frontend
