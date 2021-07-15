from bin.service import Logger
import argparse
import hashlib
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

            md5_filename = hashlib.md5(str(url).encode()).hexdigest() + '.png'
            options = argparse.Namespace(URL=None, ajax_max_timeouts='1400,1800', cookie=None, crop=None, custom_js=None, format='png', header=None, http_password=None, http_username=None, imagemagick_binary=None, input_file=None, label=False, label_bg_color='NavajoWhite', label_size=60, log_level='DEBUG', multiprotocol=False, no_error_file=False, no_xserver=False, output_directory='www/screenshots', port=None, proxy=None, proxy_auth=None, proxy_type=None, quality=75, renderer='phantomjs', renderer_binary=None, single_output_file=md5_filename, ssl=False, timeout=30, verbosity=2, window_size='1200,800', workers=4)
            take_screenshot([url], options)
            os.rename(md5_filename, 'www/screenshots/' + md5_filename)
            result['items'].append(md5_filename)

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
