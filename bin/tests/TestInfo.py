from bin.service import Info


class TestInfo:

    def __init__(self, test_path, owned_count):
        self.test_path = test_path
        self.owned_count = owned_count
        self.info = Info.Info(self.test_path)

    def run(self):

        expected_idea_count = 60 - self.owned_count
        expected_fact_count = 0 + self.owned_count
        expected_jira_count = 30
        expected_confluence_count = 30

        actual_idea_count = self.info.get_idea_count()
        actual_fact_count = self.info.get_fact_count()
        actual_jira_count = self.info.get_jira_count()
        actual_confluence_count = self.info.get_confluence_count()

        return expected_idea_count == actual_idea_count and expected_fact_count == actual_fact_count \
               and expected_jira_count == actual_jira_count and expected_confluence_count == actual_confluence_count
