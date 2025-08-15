from django import forms
from django.utils import timezone
from .models import Booking, Station, PricingPlan
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class BookingForm(forms.Form):
    station = forms.ModelChoiceField(
        queryset=Station.objects.filter(is_active=True),
        label="İstasyon"
    )
    pricing = forms.ModelChoiceField(
        queryset=PricingPlan.objects.all(),
        label="Fiyatlandırma Planı"
    )
    start_at = forms.DateTimeField(
        label="Başlangıç Zamanı",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )
    end_at = forms.DateTimeField(
        label="Bitiş Zamanı",
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        input_formats=['%Y-%m-%dT%H:%M'],
    )

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

class LoginForm(forms.Form):
    username = forms.CharField(
        label='Kullanıcı Adı',
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Kullanıcı adınızı girin'
        })
    )
    password = forms.CharField(
        label='Şifre',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Şifrenizi girin'
        })
    )
