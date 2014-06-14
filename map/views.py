
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

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100, label='')

def search(request):

    layout = request.GET.get('layout')

    if not layout:
        layout = 'vertical'

    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():

            places = place_search.text_to_nearest(form.cleaned_data['query'])
            nodes = skel.places_nodes(places)
            # nodes = skel.random_nodes(50)
            mgr = skel.MetroGraphRunner(nodes, t=10000)
            mgr.iterate_to_end()

            request.session['first_render'] = 1
            request.session['graph_json'] = mgr.mg.json()

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

