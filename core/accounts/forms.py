from django import forms

class EnableTOTPForm(forms.Form):
    confirm = forms.BooleanField(required=True, label="Enable TOTP")

class VerifyTOTPForm(forms.Form):
    totp_code = forms.CharField(max_length=6, label="Enter OTP")
    


