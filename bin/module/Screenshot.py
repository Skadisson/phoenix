from bin.service import Logger, Environment
import hashlib
import urllib.request
from webscreenshot.webscreenshot import *


class Screenshot:

    def __init__(self):
        self.logger = Logger.Logger()

    def run(self, url):

        if url == '':
            return None

        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            environment = Environment.Environment()
            user = environment.get_endpoint_confluence_user()
            password = environment.get_endpoint_confluence_password()
            if 'jira.konmedia.com' in url or 'confluence.konmedia.com' in url:
                if '?' in url:
                    url += '&os_username=' + user + '&os_password=' + password
                else:
                    url += '?os_username=' + user + '&os_password=' + password
            md5_filename = hashlib.md5(str(url).encode()).hexdigest() + '.png'
            full_path = 'www/screenshots/' + md5_filename
            one_day = 60 * 60 * 24
            if os.path.isfile(full_path) is True and (time.time() - os.stat(full_path).st_mtime) > one_day:
                os.remove(full_path)
            elif os.path.isfile(full_path) is False:
                http_code = urllib.request.urlopen("https://www.stackoverflow.com").getcode()
                if http_code == 200:
                    options = argparse.Namespace(URL=None, ajax_max_timeouts='1400,1800', cookie=None, crop=None, custom_js=None, format='png', header=None, http_password=None, http_username=None, imagemagick_binary=None, input_file=None, label=False, label_bg_color='NavajoWhite', label_size=60, log_level='ERROR', multiprotocol=False, no_error_file=False, no_xserver=False, output_directory='www/screenshots', port=None, proxy=None, proxy_auth=None, proxy_type=None, quality=75, renderer='phantomjs', renderer_binary=None, single_output_file=md5_filename, ssl=True, timeout=30, verbosity=2, window_size='1920,1080', workers=4)
                    take_screenshot([url], options)
                    os.rename(md5_filename, full_path)
                else:
                    result['success'] = False
                    result['error'] = f"Screenshot failed, URL did respond with http code {http_code}"
                    self.logger.add_entry(self.__class__.__name__, str(result['error']))
            result['items'].append(md5_filename)

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
