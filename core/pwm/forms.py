from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

class LoginForm(forms.Form):
   email = forms.CharField(max_length=65)
   password = forms.CharField(max_length=65, widget=forms.PasswordInput)
   
   
   
   
class UserRegisterForm(UserCreationForm):
   class Meta:
      model = get_user_model()
      fields = ['email']
