class Achievement:

    def __init__(self):
        self.user_id = None
        self.last_login = None
        self.logged_in = 0
        self.facts_created = 0
        self.ideas_edited = 0
        self.facts_edited = 0
        self.shout_outs_created = 0
        self.shout_outs_reacted = 0
        self.cards_clicked = 0
        self.qa_tickets_clicked = 0
        self.devops_tickets_clicked = 0
        self.product_tickets_clicked = 0
        self.service_tickets_clicked = 0
        self.favourites_created = 0
        self.favourites_deleted = 0
        self.facts_created_today = 0
        self.cards_clicked_today = 0
        self.logged_in_today = 0
        self.shout_outs_created_today = 0
        self.searches_triggered = 0
        self.searches_triggered_today = 0
        self.quests_completed = 0
        self.labels = []

    def __iter__(self):
        yield 'user_id', self.user_id
        yield 'last_login', self.last_login
        yield 'logged_in', self.logged_in
        yield 'facts_created', self.facts_created
        yield 'ideas_edited', self.ideas_edited
        yield 'facts_edited', self.facts_edited
        yield 'shout_outs_created', self.shout_outs_created
        yield 'shout_outs_reacted', self.shout_outs_reacted
        yield 'cards_clicked', self.cards_clicked
        yield 'qa_tickets_clicked', self.qa_tickets_clicked
        yield 'devops_tickets_clicked', self.devops_tickets_clicked
        yield 'product_tickets_clicked', self.product_tickets_clicked
        yield 'service_tickets_clicked', self.service_tickets_clicked
        yield 'favourites_created', self.favourites_created
        yield 'favourites_deleted', self.favourites_deleted
        yield 'facts_created_today', self.facts_created_today
        yield 'cards_clicked_today', self.cards_clicked_today
        yield 'logged_in_today', self.logged_in_today
        yield 'shout_outs_created_today', self.shout_outs_created_today
        yield 'searches_triggered', self.searches_triggered
        yield 'searches_triggered_today', self.searches_triggered_today
        yield 'quests_completed', self.quests_completed
        yield 'labels', self.labels
