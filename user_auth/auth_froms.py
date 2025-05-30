from django.forms import ModelForm
from django.contrib.auth.models import Group , Permission
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django import forms

class CreateNormalUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name' , 'password1' , 'password2']

    #custom logic for user
    def save(self , commit=True):
        user = super().save(commit)
        group = Group.objects.get(name='Customer')
        user.groups.add(group)
        return user



