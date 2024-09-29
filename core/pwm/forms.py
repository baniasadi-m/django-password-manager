from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from accounts.models import Profile
from pwm.models import WinServer
# from pwm.models import ServerSelection

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
        fields = ['user','nid', 'first_name', 'last_name',
                  'mobile','win_local_account','win_ldap_account',
                  'server'
                  ]        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['user'].disabled = True   
        self.fields['nid'].disabled = True   
        self.fields['mobile'].disabled = True   
        self.fields['win_local_account'].disabled = True   
        self.fields['win_ldap_account'].disabled = True   
  

class MobileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['mobile']        
    # def __init__(self, *args, **kwargs):
    #     super(MobileForm, self).__init__(*args, **kwargs)
        # self.fields['mobile'].queryset = self.instance.mobile
        # self.fields['mobile'].disabled = False
        
class OTPVerificationForm(forms.Form):
    otp = forms.CharField(max_length=6, required=True, label="Enter OTP")

class ResetPasswordForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['server']
    account = forms.CharField(max_length=20,label='کاربری')
    password1 = forms.CharField(widget=forms.PasswordInput(),label='پسورد جدید')
    password2 = forms.CharField(widget=forms.PasswordInput(),label='تکرار پسورد جدید')
    otp = forms.CharField(max_length=6)
        
class ProfileUserForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['user']        
    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields['user'].disabled = True    

class UserStatusForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
                  'win_ldap_account',
                  'server'
                  ]     
        # widgets = {
        #     'server': forms.HiddenInput(),  # This will hide the field in the form
        # }
        # readonly_fields = [ 'server']
    def __init__(self, *args, **kwargs):
        super(UserStatusForm, self).__init__(*args, **kwargs)
        self.fields['win_ldap_account'].widget.attrs['readonly'] = True 
        self.fields['server'].queryset = self.instance.server.__class__.objects.filter(pk=self.instance.server.pk)
        self.fields['server'].widget.attrs['readonly'] = True 
        

        