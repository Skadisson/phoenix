import yaml
import os

from yaml import CLoader as Loader


class Environment:
    """Environmental variable library"""

    def __init__(self):
        self.base_path = None
        self.init_base_path()

    def init_base_path(self):
        file_path = os.path.realpath(__file__)
        self.base_path = '\\'.join(file_path.split('\\')[0:-3]) + '\\'

    def get_service_host(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['host']

    def get_service_port(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['port']

    def get_path_jira_test_data(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['jira_test_data']

    def get_path_confluence_test_data(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['confluence_test_data']

    def get_path_jira_cache(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['jira_cache']

    def get_path_confluence_cache(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['confluence_cache']

    def get_path_card_cache(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['card_cache']

    def get_path_favourites(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['favourites']

    def get_path_log(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['log']

    def load_yaml(self, name):
        file = open("{}env\\{}.yaml".format(self.base_path, name), "r", encoding='utf8')
        return yaml.load(file, Loader=Loader)
