from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render,HttpResponse,redirect
from django.views.generic.base import TemplateView,RedirectView
from django.views.generic import View,FormView,CreateView,ListView,DetailView
from .forms import LoginForm, UserRegisterForm, UserForm, ProfileForm, ResetPasswordForm
from accounts.models.profiles import Profile
from accounts.models.users import UserTOTP,User
from .models import WinServer
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import license_check,win_account_reset_password
from .utils import WorkingHoursMixin, VerifiedUserMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib import messages
from accounts.totp_utils import verify_totp_code
import pyotp
import qrcode
from io import BytesIO

# Create your views here.


class EditProfileView(LoginRequiredMixin,VerifiedUserMixin,WorkingHoursMixin,View):
    template_name='pwm/profileedit.html'
    success_url = reverse_lazy('pwm:dashboard')
    
    def get(self,request,*args, **kwargs):
        # Initial data for the forms
        # print(request.profile)
        profile = get_object_or_404(Profile,user=request.user)
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=profile)
        # print(profile_form)
        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })
   
    def post(self,request,*args, **kwargs):
        # Handling form submissions
        print(request.user)
        profile = get_object_or_404(Profile,user=request.user)
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(data=request.POST,files=request.FILES, instance=profile)
        print(f"profile validation is: {profile_form.is_valid()}")

        if  profile_form.is_valid():
            # user_form.save()
            print(f"profile save")
            profile_form.save()
            return redirect(self.success_url)

        return render(request, self.template_name, {
            'user_form': user_form,
            'profile_form': profile_form
        })

class IndexView(WorkingHoursMixin,RedirectView):
    permanent = False
    query_string = False
    pattern_name = 'pwm:dashboard'


# class IndexView(WorkingHoursMixin,View):
#     template_name = 'pwm/login.html'
#     form_class = LoginForm
    
#     def dispatch(self, request, *args, **kwargs):
#         if not self.check_working_hours():
#             return HttpResponseForbidden("The application is closed at the moment.")
#         return super().dispatch(request, *args, **kwargs)
    
#     def get(self, request):
#         form = self.form_class
#         return render(request, self.template_name,context={'form': form})

class UserRegisterView(WorkingHoursMixin,CreateView):
    template_name = 'pwm/register.html'
    success_url = reverse_lazy('pwm:dashboard')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"
    def dispatch(self, request, *args, **kwargs):
        if not self.check_working_hours():
            return HttpResponseForbidden("The application is closed at the moment.")
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

class DashboardView(LoginRequiredMixin,WorkingHoursMixin,ListView):
    model= Profile
    context_object_name = 'profile'
    template_name = 'pwm/dashboard.html'
    
    def dispatch(self, request, *args, **kwargs):

        if self.check_working_hours()[0] == False:
            return self.check_working_hours()[1]
        return super().dispatch(request, *args, **kwargs)
    # def dispatch(self, request, *args, **kwargs):
    #     if not license_check():
    #     # If the condition is not met, return a response
    #         return HttpResponseForbidden("You are License Expired.")
    #     return super().dispatch(request, *args, **kwargs)
    
    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Profile.objects.get(user=self.request.user.id)

class ServerDetailView(LoginRequiredMixin,WorkingHoursMixin,DetailView):
    pass


class ResetPassSuccessView(LoginRequiredMixin, VerifiedUserMixin, WorkingHoursMixin,TemplateView):
    template_name = "pwm/resetpass_success.html"
    
class ResetPassView(LoginRequiredMixin,VerifiedUserMixin,WorkingHoursMixin,View):
    success_url=reverse_lazy('pwm:resetpass_success')
    template_name = 'pwm/resetpass.html'
    # form_class=ServerSelectionForm
    def get(self,request,*args, **kwargs):
        # Initial data for the forms
        # print(request.profile)
        profile = get_object_or_404(UserTOTP,user=request.user)
        print(profile.totp_secret)
        user_form = ResetPasswordForm
        
        # print(profile_form)
        return render(request, self.template_name, {
            'form': user_form,
        })
   
    def post(self,request,*args, **kwargs):
        # Handling form submissions
        request_data = {k:v[0] for k,v in dict(request.POST).items()}
        print(request.user,request_data)
        profile = get_object_or_404(Profile,user=request.user)
        if request_data['password1'] != request_data['password2']:
            messages.add_message(request,messages.ERROR,'password confirm error')
            return  redirect('pwm:resetpass')
        
        otp_user = get_object_or_404(UserTOTP,user=request.user)
        if not verify_totp_code(secret=otp_user.totp_secret, code=request_data['otp']):
            messages.add_message(request,messages.ERROR,'Otp verify error')
            return  redirect('pwm:resetpass') 
        
        server = get_object_or_404(WinServer,pk=request_data['server'])
        if server.is_ldap:
            if not profile.win_ldap_account == request_data['account']:
                messages.add_message(request,messages.ERROR,'your server/user entered not valid')
                return  redirect('pwm:resetpass')
        else:
            if not profile.win_local_account == request_data['account']:
                messages.add_message(request,messages.ERROR,'your server/user entered not valid')
                return  redirect('pwm:resetpass')                  
        if win_account_reset_password():
            return redirect(self.success_url)
                   
        # user_form = UserForm(request.POST, instance=request.user)
        # profile_form = ProfileForm(data=request.POST,files=request.FILES, instance=profile)
        # print(f"profile validation is: {profile_form.is_valid()}")

        # if  profile_form.is_valid():
        #     # user_form.save()
        #     print(f"profile save")
        #     profile_form.save()
        

        # return render(request, self.template_name, {
        #     'user_form': user_form,
        #     'profile_form': profile_form
        # })








