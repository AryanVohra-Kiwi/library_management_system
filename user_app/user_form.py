from django.forms import ModelForm
from django import forms
from .models import CustomerCreate
from django.contrib.auth.models import Group
class UserForm(forms.ModelForm):
    class Meta:
        model = CustomerCreate
        fields = ['first_name', 'last_name' , 'age' , 'phone' , 'email']

        #assigns customer group to the user when they create a form
        def save(self , commit = True):
            user = super().save(commit)
            gorup = Group.objects.get(name='Customer')
            user.groups.add(gorup)
            return user

class UpdateCustomer(forms.ModelForm):
    class Meta:
        model = CustomerCreate
        fields = '__all__'
        exclude = ['user' , 'date_joined']


