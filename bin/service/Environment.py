import yaml
import os


class Environment:
    """Environmental variable library"""

    def get_service_host(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['host']

    def get_use_ssl(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['use_ssl']

    def get_service_port(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['port_webservice']

    def get_server_port(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['port_webserver']

    def get_service_enable_git(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['enable_git'] == 1

    def get_service_shout_out_liftime_days(self):
        service_yaml = self.load_yaml('service')
        return service_yaml['shout_out_liftime_days']

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

    def get_endpoint_projects(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['projects']

    def get_endpoint_info(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['info']

    def get_endpoint_mongo_db_cloud(self):
        service_yaml = self.load_yaml('endpoint')
        return service_yaml['mongo_db_cloud']

    def load_yaml(self, name):
        path = os.path.join("env", f"{name}.yaml")
        file = open(path, "r", encoding='utf8')
        return yaml.load(file, Loader=yaml.FullLoader)

    def store_yaml(self, name, data):
        path = os.path.join("env", f"{name}.yaml")
        file = open(path, "w", encoding='utf8')
        yaml.dump(data, file, Dumper=yaml.Dumper)
