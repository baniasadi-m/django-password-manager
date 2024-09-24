from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Profile

class LoginForm(forms.Form):
   email = forms.CharField(max_length=65)
   password = forms.CharField(max_length=65, widget=forms.PasswordInput)
   
   
   
   
class UserRegisterForm(UserCreationForm):
   class Meta:
      model = get_user_model()
      fields = ['email']


class UserForm(forms.ModelForm):
    class Meta:
        model = get_user_model()
        fields = ['email']

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].disabled = True   
        
class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['nid', 'first_name', 'last_name',
                  'mobile','server','win_user','image'
                  ]        