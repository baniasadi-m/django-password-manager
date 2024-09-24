from django.shortcuts import render,get_object_or_404,redirect
from django.urls import reverse_lazy
from django.http import HttpResponse, JsonResponse
from django.views.decorators.cache import cache_page
from django.core.cache import cache
import time
from .tasks import sendEmail
import requests
from .forms import  EnableTOTPForm,VerifyTOTPForm
from django.views.generic import View, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .totp_utils import generate_totp_secret, verify_totp_code, generate_qr_code
from .models import UserTOTP
from django.core.files.base import File
from pwm.utils import WorkingHoursMixin, VerifiedUserMixin
import base64


def send_email(request):
    sendEmail.delay()
    return HttpResponse("<h1>Done Sending</h1>")


@cache_page(60)
def test(request):
    response = requests.get(
        "https://b0334311-3948-4555-af18-17d55a318926.mock.pstmn.io/test/delay/5"
    )
    return JsonResponse(response.json())



from django.contrib.auth import get_user_model

class GenerateTOTPView(LoginRequiredMixin,VerifiedUserMixin, WorkingHoursMixin, FormView):
    template_name = 'accounts/totp_generate.html'
    form_class = EnableTOTPForm
    success_url = reverse_lazy('accounts:totp_show')

    def form_valid(self, form):
        user_profile, created = UserTOTP.objects.get_or_create(user=self.request.user)
        if user_profile.qr_code_image == None and user_profile.totp_secret == None:
            secret = generate_totp_secret()
            user_profile.totp_secret = secret
            qr_image = generate_qr_code(self.request.user.email, secret)
            user_profile.qr_code_image = qr_image
            user_profile.save()
            return super().form_valid(form)
        
        return redirect(self.success_url)
            
        
        # user_profile.qr_code_image.save(f'{self.request.user.email}.png', File(qr_code_image))

        

class TOTPShowView(LoginRequiredMixin, VerifiedUserMixin, WorkingHoursMixin, TemplateView):
    template_name = 'accounts/totp_show.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserTOTP.objects.get(user=self.request.user)
        qr_code_binary = user_profile.qr_code_image
        context['qr_code_image'] = base64.b64encode(qr_code_binary).decode('utf-8')
        return context
    # form_class = EnableTOTPForm
    # success_url = reverse_lazy('accounts:totp_generate')

    # def form_valid(self, form):
    #     user_profile, created = UserTOTP.objects.get_or_create(user=self.request.user)
    #     secret = generate_totp_secret()
    #     user_profile.totp_secret = secret
    #     qr_image = generate_qr_code(self.request.user.email, secret)
    #     # user_profile.qr_code_image.save(f'{self.request.user.email}.png', File(qr_code_image))
    #     user_profile.qr_code_image = qr_image
    #     user_profile.save()
    #     return super().form_valid(form)
    
class VerifyTOTPView(LoginRequiredMixin, VerifiedUserMixin, WorkingHoursMixin, FormView):
    template_name = 'accounts/totp_verify.html'
    form_class = VerifyTOTPForm
    success_url = reverse_lazy('accounts:totp_success')

    def form_valid(self, form):
        user_profile = UserTOTP.objects.get(user=self.request.user)
        code = form.cleaned_data.get('totp_code')
        print(code,verify_totp_code(user_profile.totp_secret, code))
        if verify_totp_code(user_profile.totp_secret, code):
            return super().form_valid(form)
        else:
            form.add_error('totp_code', 'Invalid Code')
            return self.form_invalid(form)
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_profile = UserTOTP.objects.get(user=self.request.user)
        # generate_qr_code(username=user_profile.user, secret=user_profile.totp_secret)
        context['qr_code_image'] = user_profile.qr_code_image
        return context
    
    # def post(self,request,*args, **kwargs):
    #     print(request.user)
    
class TOTPSuccessView(LoginRequiredMixin, VerifiedUserMixin, WorkingHoursMixin, TemplateView):
    template_name = 'accounts/totp_success.html'