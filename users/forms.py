from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class SignUpForm(UserCreationForm):

    # I added this function so that the email is unique
    def clean_email(self):
        """This function return an error message if the email has already been taken"""

        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Cet Email à déjà été pris.')
        return email

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

class ConnexionForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)


class EditProfileForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur")
    about_me = forms.CharField(widget=forms.Textarea(attrs={'style':'width: 100%;'}), label='A propos de moi')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username


    # This function ensures that when the user changes his username, he does not take the one of another
    def clean_username(self):
        """This function return an error message if the username has already been taken"""

        username = self.cleaned_data['username']
        if username != self.original_username:
            # The user can not take a username if it is already in the database
            if User.objects.filter(username=username).exists():
                raise forms.ValidationError('Ce nom d\'utilisateur est déjà pris.')
        return username