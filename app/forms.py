from django import forms
from app.models import User


class SelectUsername(forms.Form):
    """
    Form for selecting username.
    """
    name = forms.CharField(max_length=150, required=True)

    def clean_name(self):
        """
        Makes sure we have a unique username.
        """
        name = self.cleaned_data.get('name')
        if User.objects.filter(name=name).exists():
            raise forms.ValidationError("This username already exists")
        return name

