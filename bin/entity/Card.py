class Card:

    def __init__(self):
        self.id = None
        self.created = None
        self.changed = None
        self.author = None
        self.text = None
        self.title = None
        self.type = None
        self.relation_id = None
        self.relation_type = None
        self.editors = None
        self.keywords = None
        self.clicks = 0
        self.likes = 0
        self.external_link = None
        self.screenshot = None

    def __iter__(self):
        yield 'id', self.id
        yield 'created', self.created
        yield 'changed', self.changed
        yield 'author', self.author
        yield 'text', self.text
        yield 'title', self.title
        yield 'type', self.type
        yield 'relation_id', self.relation_id
        yield 'relation_type', self.relation_type
        yield 'editors', self.editors
        yield 'keywords', self.keywords
        yield 'clicks', self.clicks
        yield 'likes', self.likes
        yield 'external_link', self.external_link
        yield 'screenshot', self.screenshot
