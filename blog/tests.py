from django.test import TestCase
from blog.models import Comment
from django.contrib.auth.models import User
from catalog.models import Substitute


class CommentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )
        self.substitute = Substitute.objects.create(name='substitute1', picture='picture')
        Comment.objects.create(content='test', author=self.user, substitute=self.substitute)

    
    def test_object_name(self):
        comment = Comment.objects.get(content='test')
        expected_object_name = f'{self.user.username}'
        self.assertEquals(expected_object_name, str(comment))