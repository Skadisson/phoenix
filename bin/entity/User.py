class User:

    def __init__(self):
        self.id = None
        self.alias = None
        self.name = None
        self.password = None
        self.created = None
        self.changed = None
        self.active = None

    def __iter__(self):
        yield 'id', self.id
        yield 'alias', self.alias
        yield 'name', self.name
        yield 'password', self.password
        yield 'created', self.created
        yield 'changed', self.changed
        yield 'active', self.active
