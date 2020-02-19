import collections


class Library:

    def __init__(self):
        self.words = collections.Counter()
        self.index = []

    def add_tickets(self, tickets):
        for ticket_id in tickets:
            ticket = tickets[ticket_id]
            if 'Comments' in ticket and ticket['Comments'] is not None:
                for comment in ticket['Comments']:
                    count = int(ticket['Comments'][comment])
                    self.add_word(str(comment), count)
            if 'Keywords' in ticket and ticket['Keywords'] is not None:
                self.add_words(ticket['Keywords'])

    def add_text(self, text):
        words = text.split()
        self.add_words(words)

    def add_words(self, words):
        for word in words:
            self.add_word(str(word))

    def add_word(self, word, count=1):
        self.words.update({str(word), count})
        if word not in self.index:
            self.index.append(word)

    def get_words(self):
        return self.words

    def get_index(self, word):
        if word in self.index:
            return self.index.index(word)
        return -1
