from django import forms
from bootstrap_toolkit.widgets import BootstrapDateInput, BootstrapTextInput, BootstrapUneditableInput

class SearchForm(forms.Form):
    Place = forms.CharField(
        max_length=100,
        widget=BootstrapTextInput()
    )

    Radius = forms.FloatField(
        widget=BootstrapTextInput()
    )