from bin.service import Info, Logger, Sync
import time


class SyncState:

    def __init__(self):
        self.info = Info.Info()
        self.logger = Logger.Logger()
        self.sync = Sync.Sync()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:

            data = self.sync.load_yaml()
            if data is None:
                data = {'last': time.time(), 'average': 0, 'runtimes': [], 'running': False}
            result['items'].append(data)

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
