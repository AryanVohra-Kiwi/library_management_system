from django import forms
from .models import BookStructure
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