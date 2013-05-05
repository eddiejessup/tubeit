from __future__ import print_function
import urllib
import json
import httplib

class Searcher(object):
    def __init__(self):
        self.get_path_base()
        self.conn = httplib.HTTPSConnection(self.HOST)

    def get_path_base(self):
        self.path_base = '/%s?%s' % (self.API_PATH, urllib.urlencode(self.args_base))

    def get_response(self, args):
        request_path = '%s&%s' % (self.path_base, urllib.urlencode(args))
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

    def search(self, lat, long, rad):
        args = {
            'location': '%s,%s' % (lat, long),
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
        lat, long = location(rt['results'][0])
    except IndexError:
        print(rt)
        raise Exception
    return lat, long

def text_to_nearby(query, rad=100.0):
    lat, long = text_to_loc(query)
    sn = NearbySearcher()
    rn = sn.search(lat, long, rad)
    return rn['results']

def text_to_nearest(query, rad_0=100.0):
    lat, long = text_to_loc(query)
    sn = NearbySearcher()
    rad = rad_0
    for _ in range(10):
        rn = sn.search(lat, long, rad)
        if len(rn['results']) > 18: break
        rad *= 2
    return rn['results']

def plot(query, rad=100.0):
    import matplotlib.pyplot as pp
    rn = text_to_nearby(query, rad)
    for place in rn:
        lat, long = location(place)
        pp.scatter(lat, long)
        pp.text(lat, long, place['name'])
    pp.show()