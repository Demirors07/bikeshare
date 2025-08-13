from django import forms
from django.utils import timezone
from .models import Booking, Station, PricingPlan
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class BookingForm(forms.Form):
    station = forms.ModelChoiceField(queryset=Station.objects.filter(is_active=True))
    pricing = forms.ModelChoiceField(queryset=PricingPlan.objects.all())
    start_at = forms.DateTimeField(help_text="YYYY-MM-DD HH:MM")
    end_at = forms.DateTimeField(help_text="YYYY-MM-DD HH:MM")

    def clean(self):
        data = super().clean()
        if "start_at" in data and "end_at" in data and data["end_at"] <= data["start_at"]:
            raise forms.ValidationError("Bitiş tarihi başlangıçtan sonra olmalı.")
        return data

class ReturnConfirmForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Fiziksel teslimi onaylıyorum")

class SignUpForm(UserCreationForm):
    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")
