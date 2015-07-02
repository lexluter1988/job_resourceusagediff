__author__ = 'lexluter1988'
class Api:
    def __init__(self, connection):
        self.connection = connection

    def execute(self, method, **params):
        response = getattr(self.connection, method)(params) # Hack from poaupdater
        if response['status'] != 0:
            self.txn_id = None
            raise Exception('Method {0} returned non-zero status {1} and\
                             error {2}'.format(method, response['status'], response['error_message']))
        else:
            return response.get('result', None)
