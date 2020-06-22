from bin.service import Logger, ShoutOutStorage


class ShoutOuts:

    def __init__(self):
        self.logger = Logger.Logger()
        self.so_storage = ShoutOutStorage.ShoutOutStorage()

    def run(self):
        result = {
            'items': [],
            'success': True,
            'error': None
        }
        try:
            found_shout_outs = []
            shout_outs = self.so_storage.get_shout_outs()
            for shout_out in shout_outs:
                if '_id' in shout_out:
                    del(shout_out['_id'])
                found_shout_outs.append(shout_out)
            result['items'].append({
                'shout_outs': found_shout_outs
            })

        except Exception as e:
            result['error'] = str(e)
            result['success'] = False
            self.logger.add_entry(self.__class__.__name__, e)

        return result
