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

    def get_path_log(self):
        path_yaml = self.load_yaml('path')
        return path_yaml['log']

    def get_endpoint_git_projects(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['git_projects']

    def get_endpoint_git_commits(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['git_commits']

    def get_endpoint_git_private_token(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['git_private_token']

    def get_endpoint_confluence_user(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['confluence_user']

    def get_endpoint_confluence_password(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['confluence_password']

    def get_endpoint_confluence_host(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['confluence_host']

    def get_map_confluence_spaces(self):
        service_yaml = self.load_yaml('map')
        return service_yaml['confluence_spaces']

    def get_path_private_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['private_key']

    def get_path_public_key(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['public_key']

    def get_path_token(self):
        service_yaml = self.load_yaml('path')
        return service_yaml['token']

    def get_endpoint_consumer_key(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['consumer_key']

    def get_endpoint_consumer_secret(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['consumer_secret']

    def get_endpoint_request_token(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['request_token']

    def get_endpoint_access_token(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['access_token']

    def get_endpoint_authorize(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['authorize']

    def get_endpoint_ticket(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['ticket']

    def get_endpoint_tickets(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['tickets']

    def get_endpoint_info(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['info']

    def load_yaml(self, name):
        file = open("{}env\\{}.yaml".format(self.base_path, name), "r", encoding='utf8')
        return yaml.load(file, Loader=Loader)
