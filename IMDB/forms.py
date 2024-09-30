from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from IMDB.models import *

# form special pentru înregistrarea unui User in baza de date. E bazat pe UserCreationForm din Django.
class RegistrationForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class DatasetUploadForm(forms.ModelForm):
    class Meta:
        model = Dataset
        fields = ['name', 'file']        
