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

class IssueBookModelForm(forms.ModelForm):
    class Meta:
        model = IssueBook
        exclude = ('book','issued_by')

    #get yhe issue date when the function is initialized
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'Issue_date' in self.initial:
            issue_date = self.initial['Issue_date']
        else:
            issue_date = datetime.date.today()
        self.fields['Issue_date'].initial = issue_date
        self.fields['Return_date'].initial = issue_date + datetime.timedelta(days=7)
        self.fields['Return_date'].widget.attrs['readonly'] = True
    #make sure return date is not more than 7 days
    def clean(self):
        cleaned_data = super().clean()
        issue_date = cleaned_data.get('Issue_date')
        if issue_date:
            cleaned_data['Return_date'] = issue_date + datetime.timedelta(days=7)
        else:
            self.add_error('Issue_date', 'Issue date is required.')
        return cleaned_data

