class User:

    def __init__(self):
        self.id = None
        self.name = None
        self.short = None

    def __iter__(self):
        yield 'id', self.id
        yield 'name', self.name
        yield 'short', self.short
