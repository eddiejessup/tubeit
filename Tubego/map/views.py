from __future__ import print_function
import json
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from map import place_search
from map import skel
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template.context import RequestContext

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)

def search(request):
    layout = request.GET.get('layout')

    if not layout:
        layout = 'vertical'

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            places = place_search.text_to_nearest(form.cleaned_data['query'])
            #request.GET = request.GET.copy()
            #request.GET.update({'places':places})
            #print(request.GET.get('places'))
            #return render(request, 'map_load.html', {'places': places})]
            g = skel.places_graph(places)
            skel.normalise_rs(g)
            skel.grow(g)
            skel.simplify(g, 10000)
            g_json = skel.jsonned(g)
            return render(request, 'draw.html', {'graph': g_json})
    else:
        form = SearchForm()

    return render_to_response('search.html', RequestContext(request, {
        'form': form,
        'layout': layout,
    }))

def draw(request):
    return HttpResponseRedirect('hi')