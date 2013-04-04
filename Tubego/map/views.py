from __future__ import print_function
from django import forms
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse

from map import place_search

class SearchForm(forms.Form):
    query = forms.CharField(max_length=100)
    r = forms.FloatField()

def search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            places = place_search.text_to_nearby(form.cleaned_data['query'], form.cleaned_data['r'])
            return render(request, 'draw.html', {'places': places})
    else:
        form = SearchForm()
    print(reverse('search'))
    return render(request, 'search.html', {'form': form})
#    return render(request, reverse('search'), {'form': form})

def draw(request):
    return HttpResponseRedirect('hi')