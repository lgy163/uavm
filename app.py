# examples/things.py
import json
# Let's get this party started!
from wsgiref.simple_server import make_server

import falcon

from fusionsearch import FusionSearcher


# Falcon follows the REST architectural style, meaning (among
# other things) that you think in terms of resources and state
# transitions, which map to HTTP verbs.
class ThingsResource:
    def on_get(self, req, resp):
        """Handles GET requests"""
        resp.status = falcon.HTTP_200  # This is the default status
        resp.content_type = falcon.MEDIA_TEXT  # Default is JSON, so override
        resp.text = (
            '\nTwo things awe me most, the starry sky '
            'above me and the moral law within me.\n'
            '\n'
            '    ~ Immanuel Kant\n\n'
        )


class Searcher:
    def on_get(self, req, resp):
        search_type = req.get_param('type')
        size = req.get_param('size')
        key = req.get_param('key')
        fs = FusionSearcher()
        resp.status = falcon.HTTP_200  # This is the default status
        resp.text = json.dumps(fs.search(key, search_type, size=size))


# falcon.App instances are callable WSGI apps
# in larger applications the app is created in a separate file
app = falcon.App()

# Resources are represented by long-lived class instances
things = ThingsResource()
searcher = Searcher()
# things will handle all requests to the '/things' URL path
app.add_route('/things', things)
app.add_route('/search', searcher)

if __name__ == '__main__':
    with make_server('', 8000, app) as httpd:
        print('Serving on port 8000...')

        # Serve until process is killed
        httpd.serve_forever()
