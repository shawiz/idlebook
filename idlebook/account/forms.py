import urllib2
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from django import forms as forms
from django.core import validators
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from models import UserProfile, Wallet, EmailConfirmation
from notifications import NotificationSettings
from idlebook.network.models import Network
from idlebook import settings


class StartForm(forms.Form):
    email = forms.CharField(label='Email', max_length=30, required=True)
    
    def clean_email(self):
        data = '%s@uw.edu' % self.cleaned_data['email']
        try:
            User.objects.get(email=data)
        except User.DoesNotExist:
            return data
        raise validators.ValidationError('The email "%s" has already exist.' % data)


class SignupForm(forms.Form):
    first_name = forms.CharField(label='First Name', max_length=30)
    last_name = forms.CharField(label='Last Name', max_length=30)
    email = forms.CharField(label='Email', max_length=30, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(render_value=False), required=True)

    def clean_email(self):
        data = '%s@uw.edu' % self.cleaned_data['email']
        try:
            User.objects.get(email=data)
        except User.DoesNotExist:
            return data
        raise validators.ValidationError('The email "%s" has already exist.' % data)

    def save(self):
        new_user = User.objects.create_user(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password']
        )
        new_user.first_name = self.cleaned_data['first_name']
        new_user.last_name = self.cleaned_data['last_name']
        new_user.save()
        new_username = int(new_user.id) + 1000000
                
        # set network for the user after registration
        # todo: make it universal for all universities using email pattern        
        network = Network.objects.get(id=1)
        profile = UserProfile(user=new_user, username=new_username, network=network)
        profile.save()
        wallet = Wallet(user=new_user)
        wallet.save()
        notif_setting = NotificationSettings(user=new_user)
        notif_setting.save()
        

        # send email confirmation / only for debug, so no use
        #EmailConfirmation.objects.send_confirmation(self.cleaned_data['email'], profile)

        return new_user


class FacebookSignupForm(forms.Form):
    email = forms.CharField(label='Email', max_length=30, required=True)

    def clean_email(self):
        data = '%s@uw.edu' % self.cleaned_data['email']
        try:
            User.objects.get(email=data)
        except User.DoesNotExist:
            return data
        raise validators.ValidationError('The email "%s" has already exist.' % data)

    def save(self, facebook_data):
        new_user = User.objects.create(
            username=self.cleaned_data['email'],
            email=self.cleaned_data['email']
        )
        new_user.first_name = facebook_data['first_name']
        new_user.last_name = facebook_data['last_name']
        
        new_user.save()
        new_user.set_unusable_password()
        new_username = int(new_user.id) + 1000000
                
        # set network for the user after registration
        # todo: make it universal for all universities using email pattern        
        network = Network.objects.get(id=1)
        
        profile = UserProfile(
            user=new_user,
            username=new_username,
            network=network
        )
        profile.save()
        
        wallet = Wallet(user=new_user)
        wallet.save()
        
        notif_setting = NotificationSettings(user=new_user)
        notif_setting.save()
                
        # send email confirmation
        EmailConfirmation.objects.send_confirmation(self.cleaned_data['email'], profile)
        
        return new_user


class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', max_length=40, required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput(render_value=False), required=True)


class ProfileForm(forms.Form):
#    first_name = forms.CharField(label='First Name', max_length=30, required=True)
#    last_name = forms.CharField(label='Last Name', max_length=30, required=True)
    about = forms.CharField(label='About Me', widget=forms.widgets.Textarea(), required=False)
    rules = forms.CharField(label='Rental Conditions', widget=forms.widgets.Textarea(), required=False)
    
    def save(self, user):
#        user.first_name = self.cleaned_data['first_name'].strip()
#        user.last_name = self.cleaned_data['last_name'].strip()
#        user.save()
        user.profile.about = self.cleaned_data['about']
        user.profile.rules = self.cleaned_data['rules'].strip()
        user.profile.save()

class NotificationForm(forms.ModelForm):
    class Meta:
        model = NotificationSettings
        exclude = ('user', 'contact_us_pickup', 'contact_us_refund', 'book_due',)
    