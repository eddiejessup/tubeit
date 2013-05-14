from __future__ import print_function
import json
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.shortcuts import render_to_response
from django.shortcuts import redirect
from django.template.context import RequestContext
from map import place_search
from map import skel
from map import metrograph as mg

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label='')

def search(request):

    layout = request.GET.get('layout')

    if not layout:
        layout = 'vertical'

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            # places = place_search.text_to_nearest(form.cleaned_data['query'])
            # g = skel.places_graph(places)

            g = skel.random_graph(g_nodes=50)
            import numpy as np
            skel.normalise_rs(g)
            skel.grow(g)
            mg.simplify(g, 1.0, 0.02, 10000)
            g_json = skel.jsonned(g)

            request.session['first_render'] = 1
            request.session['graph_json'] = g_json

            return redirect('draw')
    else:
        form = SearchForm()

    return render_to_response('search.html', RequestContext(request, {
        'form': form,
        'layout': layout,
    }))

def draw(request):
    g_json = request.session.get('graph_json')
    first_render = request.session.get('first_render')
    request.session['first_render'] = 0
    return render(request, 'draw.html', {'graph': g_json, 'animate':first_render})

