import re
from io import StringIO
from html.parser import HTMLParser


class MLStripper(HTMLParser):

    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()

    def handle_data(self, d):
        self.text.write(d)

    def get_data(self):
        return self.text.getvalue()


class RegEx:

    def __init__(self):
        self.jira_user = r"\[\~[^]]*\]"
        self.email = r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"
        self.phone = r"[0-9]* +\/ +[0-9 ]*"
        self.image = r"\.(jpg|jpeg|png|gif)$"

    def mask_texts(self, texts):
        masked_texts = []
        for text in texts:
            masked_text = self.mask_text(text)
            masked_texts.append(masked_text)
        return masked_texts

    def mask_text(self, text):
        masked_text = str(text)
        masked_text = self.strip_tags(masked_text)
        masked_text = self.mask_jira_users(masked_text)
        masked_text = self.mask_email(masked_text)
        masked_text = self.mask_phone(masked_text)
        return masked_text

    @staticmethod
    def strip_tags(text):
        s = MLStripper()
        s.feed(text)
        return s.get_data()

    def mask_jira_users(self, text):
        masked_text = re.sub(self.jira_user, '[user]', text)
        return masked_text

    def mask_email(self, text):
        masked_text = re.sub(self.email, '[email]', text)
        return masked_text

    def mask_phone(self, text):
        masked_text = re.sub(self.phone, '[phone]', text)
        return masked_text

    def is_image(self, url):
        matches = re.match(self.image, url)
        return matches is not False
