from __future__ import print_function
import json
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from map import place_search
from map import skel
from django.shortcuts import render_to_response
from django.template.context import RequestContext

from .forms import SearchForm

# def search(request):
#     if request.method == 'POST':
#         form = SearchForm(request.POST)
#         if form.is_valid():
#             places = place_search.text_to_nearby(form.cleaned_data['query'], form.cleaned_data['r'])
#             net = skel.places_to_network(places)
#             net_json = json.dumps(net, default=skel.JSONHandler)
#             return render(request, 'draw.html', {'network': net_json})
#     else:
#         form = SearchForm()
#     return render(request, 'search.html', {'form': form})

def draw(request):
    return HttpResponseRedirect('hi')

def search(request):

    layout = request.GET.get('layout')
    if not layout:
        layout = 'vertical'
    if request.method == 'POST':
        form = SearchForm(request.POST)
        form.is_valid()
        if form.is_valid:
            places = place_search.text_to_nearby(form.cleaned_data['Place'], form.cleaned_data['Radius'])
            net = skel.places_to_network(places)
            net_json = json.dumps(net, default=skel.JSONHandler)
            return render(request, 'draw.html', {'network': net_json})
    else:
        form = SearchForm()
    #return render(request, 'search.html', {'form': form})
    modelform = SearchForm()
    return render_to_response('search.html', RequestContext(request, {
        'form': form,
        'layout': layout,
    }))
