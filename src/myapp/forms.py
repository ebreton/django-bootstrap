from django import forms

from log_utils import FormLoggingMixin
from .models import Greeting


class GreetingForm(FormLoggingMixin, forms.ModelForm):
    class Meta:
        model = Greeting
        fields = ['name']
