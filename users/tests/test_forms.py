from django.test import TestCase
from django.contrib.auth.models import User
from users.forms import SignUpForm, EditProfileForm


class SignUpFormTest(TestCase):
    def test_email_already_taken(self):
        self.jacob = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )
        form = SignUpForm(data={
            'username': 'test',
            'email': 'jacob@hotmail.com',
            'password1': 'test12345',
            'password2': 'test12345'
            })
        self.assertFalse(form.is_valid())


class EditProfileFormTest(TestCase):
    def test_username_already_taken(self):
        self.jacob = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )
        
        form = EditProfileForm(data={
            'username': 'jacob',
            'about_me': 'somthing about me'
        }, original_username='user')
        self.assertFalse(form.is_valid())