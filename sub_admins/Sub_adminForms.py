from django.forms import ModelForm
from django.contrib.auth.models import Group , Permission
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordResetForm, PasswordChangeForm
from django import forms

class CreateSubAdminForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name' , 'password1' , 'password2']


        #custom logic for subadmins
    def save(self, commit=True):
        user = super().save(commit)
        group = Group.objects.get(name='sub-admin')
        user.groups.add(group)
        return user

class UpdateSubAdminForm(UserCreationForm):

    class Meta:
        model = User
        fields = ['username' , 'first_name' , 'last_name' , 'password1' , 'password2']


        #custom logic for subadmins
        def clean_username(self):
            username = self.cleaned_data['username']
            if User.objects.filter(username=username).exclude(id=self.instance.id).exists():
                raise forms.ValidationError('This username is already in use.')
            return username

class PasswordResetForm(PasswordChangeForm):
    class Meta:
        model = User
        fields = '__all__'



