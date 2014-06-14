
import urllib.request, urllib.parse, urllib.error
import json
import http.client

class Searcher(object):
    def __init__(self):
        self.get_path_base()
        self.conn = http.client.HTTPSConnection(self.HOST)

    def get_path_base(self):
        self.path_base = '/%s?%s' % (self.API_PATH, urllib.parse.urlencode(self.args_base))

    def get_response(self, args):
        request_path = '%s&%s' % (self.path_base, urllib.parse.urlencode(args))
        self.conn.request('GET', request_path)
        response = self.conn.getresponse()
        body = response.read()
        results = json.loads(body)
        return results

class PlacesSearcher(Searcher):
    HOST = 'maps.googleapis.com'
    API_PATH_BASE = 'maps/api/place'
    API_OUTPUT = 'json'
    API_NAME = None
    API_KEY = 'AIzaSyDfxwVqLxWLzZ0Hp6Aw38zKw03FAnZa4d4'
    args_base = {
        'key': API_KEY,
        'sensor': 'false',
    }

    def __init__(self, *args, **kwargs):
        self.API_PATH = '%s/%s/%s' % (self.API_PATH_BASE, self.API_NAME, self.API_OUTPUT)
        super(PlacesSearcher, self).__init__(*args, **kwargs)

class AutocompleteSearcher(PlacesSearcher):
    API_NAME = 'autocomplete'

    def display_results(self, r):
        places = r['predictions']
        for entry in places:
            print(entry)
            print()

    def search(self, query):
        args = {
            'input': query,
        }
        results = self.get_response(args)
        return results

class DetailSearcher(PlacesSearcher):
    API_NAME = 'details'

    def display_results(self, r):
        r = r['result']
        print(r['geometry'])
        print(r['name'])

    def search(self, query):
        args = {
            'reference': query,
        }
        results = self.get_response(args)
        return results

class NearbySearcher(PlacesSearcher):
    API_NAME = 'nearbysearch'

    def display_results(self, r):
        r = r['results']
        print(r)

    def search(self, lat, longit, rad):
        args = {
            'location': '%s,%s' % (lat, longit),
            'radius': rad,
            'types': 'bar',
        }
        results = self.get_response(args)
        return results

class TextSearcher(PlacesSearcher):
    API_NAME = 'textsearch'

    def display_results(self, r):
        r = r['results']
        print(r)

    def search(self, query):
        args = {
            'query': query,
        }
        results = self.get_response(args)
        return results

def location(r):
    return tuple(r['geometry']['location'].values())

def text_to_loc(query):
    st = TextSearcher()
    rt = st.search(query)
    try:
        lat, longit = location(rt['results'][0])
    except IndexError:
        print(rt)
        raise Exception
    return lat, longit

def text_to_nearby(query, rad=100.0):
    lat, longit = text_to_loc(query)
    sn = NearbySearcher()
    rn = sn.search(lat, longit, rad)
    return rn['results']

def text_to_nearest(query, rad_0=100.0):
    lat, longit = text_to_loc(query)
    sn = NearbySearcher()
    rad = rad_0
    for _ in range(10):
        rn = sn.search(lat, longit, rad)
        if len(rn['results']) > 40: break
        rad *= 2
    return rn['results']

def plot(query, rad=100.0):
    import matplotlib.pyplot as pp
    rn = text_to_nearby(query, rad)
    for place in rn:
        lat, longit = location(place)
        pp.scatter(lat, longit)
        pp.text(lat, longit, place['name'])
    pp.show()
