from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):

    # I added this function so that the email is unique
    def clean_email(self):
        """This function return an error message if the email has already been taken"""

        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet Email à déjà été pris')
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)