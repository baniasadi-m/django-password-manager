from typing import Any
from django.db.models.query import QuerySet
from django.forms import BaseModelForm
from django.shortcuts import render,HttpResponse,redirect
from django.views.generic.base import TemplateView,RedirectView
from django.views.generic import View,FormView,CreateView,ListView,DetailView
from .forms import LoginForm,UserRegisterForm
from accounts.models.profiles import Profile
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .utils import license_check
from .utils import WorkingHoursMixin
from django.http import HttpResponseForbidden
# Create your views here.



def index(request):
    return HttpResponse('Hello index fbv')


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
    success_url = reverse_lazy('pwm:index')
    form_class = UserRegisterForm
    success_message = "Your profile was created successfully"
    def dispatch(self, request, *args, **kwargs):
        if not self.check_working_hours():
            return HttpResponseForbidden("The application is closed at the moment.")
        return super().dispatch(request, *args, **kwargs)
    
    # def dispatch(self, request, *args, **kwargs):
    #     if not license_check():
    #     # If the condition is not met, return a response
    #         return HttpResponseForbidden("You are License Expired.")
    #     return super().dispatch(request, *args, **kwargs)
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

        




