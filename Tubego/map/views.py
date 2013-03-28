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
            points = skel.places_to_points(places)
            net = skel.points_to_network(points)
            net_json = json.dumps(net, default=skel.JSONHandler)
            return render(request, 'draw.html', {'network': net_json})
    else:
        form = SearchForm()
    print(reverse('search'))
    return render(request, 'search.html', {'form': form})

def draw(request):
    return HttpResponseRedirect('hi')