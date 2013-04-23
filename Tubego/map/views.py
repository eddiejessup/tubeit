from __future__ import print_function
import json
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from map import place_search
from map import skel

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)
    r = forms.FloatField()

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            places = place_search.text_to_nearby(form.cleaned_data['query'], form.cleaned_data['r'])
            g = skel.places_graph(places)
            skel.normalise_rs(g)
            skel.grow(g)
            for _ in range(100): skel.simplify(g)
            g_json = skel.jsonned(g)
            return render(request, 'draw.html', {'graph': g_json})
    else:
        form = SearchForm()
    return render(request, 'search.html', {'form': form})

def draw(request):
    return HttpResponseRedirect('hi')
