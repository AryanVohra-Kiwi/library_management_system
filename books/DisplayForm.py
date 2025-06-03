from django import forms
from .models import BookStructure , IssueBook
import datetime
class CreateBookModelForm(forms.ModelForm):
    class Meta:
        model = BookStructure
        fields = '__all__'

class UpdateBookModelForm(forms.ModelForm):
    class Meta:
        model = BookStructure
        fields = '__all__'

    def __init__(self , *args , **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.required = False

class IssueBookModelForm(forms.Form):
    Title = forms.CharField(max_length=100 , required=True)
    IssueDate = forms.DateField(required=True , initial=datetime.date.today)
    Return_date = forms.DateField(widget=forms.HiddenInput())

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'IssueDate' in self.initial:
            issue_date = self.initial['IssueDate']
        else:
            issue_date = datetime.date.today()
        self.fields['IssueDate'] = issue_date +datetime.timedelta(days=7)


    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('IssueDate')
        if issue_date:
            cleaned_data['Return_date'] = issue_date + datetime.timedelta(days=7)
        else:
            self.add_error('IssueDate', 'Issue date is required.')
        return cleaned_data

