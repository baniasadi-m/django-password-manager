from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render,HttpResponse,redirect
from django.views.generic.base import TemplateView,RedirectView
from django.views.generic import View,FormView,CreateView,ListView,DetailView
from .forms import LoginForm, UserRegisterForm, UserForm, ProfileForm
from accounts.models.profiles import Profile
from accounts.models.users import UserTOTP,User
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import license_check
from .utils import WorkingHoursMixin
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
import pyotp
import qrcode
from io import BytesIO

# Create your views here.



def index(request):
    return HttpResponse('Hello index fbv')

class EditProfileView(LoginRequiredMixin,WorkingHoursMixin,View):
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


class IndexView(WorkingHoursMixin,View):
    template_name = 'pwm/login.html'
    form_class = LoginForm
    
    def dispatch(self, request, *args, **kwargs):
        if not self.check_working_hours():
            return HttpResponseForbidden("The application is closed at the moment.")
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        form = self.form_class
        return render(request, self.template_name,context={'form': form})

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



class GenerateQRCodeView(LoginRequiredMixin,WorkingHoursMixin, View):
    def get(self, request):
        user =  get_object_or_404(User,user=request.user)
        # Check if the user has a TOTP secret; if not, generate one
        try:
            user_totp = user.usertotp
        except UserTOTP.DoesNotExist:
            secret = pyotp.random_base32()
            user_totp = UserTOTP.objects.create(user=user, totp_secret=secret)

        # Generate TOTP URI for Google Authenticator
        totp = pyotp.TOTP(user_totp.totp_secret)
        totp_uri = totp.provisioning_uri(user.email, issuer_name="AqrPWM")

        # Generate a QR code from the TOTP URI
        qr = qrcode.make(totp_uri)
        buffer = BytesIO()
        qr.save(buffer)
        buffer.seek(0)
        return HttpResponse(buffer, content_type="image/png")




