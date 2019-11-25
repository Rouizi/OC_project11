from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from catalog.models import Category, Product, Substitute
from blog.models import Comment
from users.models import EditProfile


class SignUpViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_signup_returns_200(self):
        response = self.client.get(reverse('users:signup'))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'users/signup.html')

    def test_redirect_if_user_is_authenticated(self):
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('users:signup'))
        self.assertRedirects(response, reverse('index'))
    def test_new_user_is_registred(self):
        # We can check that a user has been registred by trying to find it in the database but I prefer the method with count()
        nb_users_old = User.objects.count() # count users before a request
        self.client.post(reverse('users:signup'), {
            'username': 'test',
            'email': 'test@hotmail.com',
            'password1': 'test12345',
            'password2': 'test12345'
        })
        nb_users_new = User.objects.count() # count users after
        self.assertEqual(nb_users_new, nb_users_old + 1) # make sure 1 user was added


class LoginViewTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_login_returns_200(self):
        response = self.client.get(reverse('users:log_in'))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'users/login.html')

    def test_login_user(self):
        response = self.client.post(reverse('users:log_in'), {'username': 'jacob', 'password': 'top_secret'}, follow=True)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'jacob')
        # Check that the user is redirected if the connection is successful
        self.assertRedirects(response, reverse('index'))
        response = self.client.get(reverse('users:log_in'))
        # Check if the user is already logged in he will be redirected to the home page
        self.assertRedirects(response, reverse('index'))

    def test_user_redirected_to_url_contained_in_next_parameter(self):
        response = self.client.post('http://127.0.0.1:8000/users/log_in/?next=/users/profile/', 
                                    {'username': 'jacob', 'password': 'top_secret'})
        # Check our user is redirected to the profile view
        self.assertRedirects(response, reverse('users:profile'))


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_logout_user(self):
        response = self.client.get(reverse('users:log_out'), follow=True)
        # Check our user is logged out
        self.assertEqual(str(response.context['user']), 'AnonymousUser')
        # Check that the user is redirected to the log_in view if the logout is successful
        self.assertRedirects(response, reverse('users:log_in'))

class ProfileViewTest(TestCase):
    def setUp(self):
        self.jacob = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )
        self.user = User.objects.create_user(
            username='user', email='user@hotmail.com', password='top_secret'
        )
        self.substitute = Substitute.objects.create(name='substitute1', picture='picture')
        self.comment_jacob = Comment.objects.create(content='Hi I am jacob', author=self.jacob, substitute=self.substitute)
        self.comment_user = Comment.objects.create(content='Hi I am user', author=self.user, substitute=self.substitute)

    def test_profile_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('users:profile'))
        # Check that the user is redirected to the log_in view with a 'next' parameter if he is not logged in
        self.assertRedirects(response, '/users/log_in/?next=/users/profile/')

    def test_profile_returns_200(self):
        # Connect the user
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('users:profile'))
        # Check that we got a response 'success'
        self.assertEqual(response.status_code, 200)

    def test_profile_view_returns_profile_of_current_user(self):
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('users:profile'))
        # Check we got the profile of the current user
        self.assertEqual(response.context['current_user'], self.jacob)
        # Check that we got the comment of the user 'jacob'
        self.assertEqual(response.context['comments'][0].content, 'Hi I am jacob')

    def test_profile_view_returns_profile_of_a_given_user(self):
        # Connect with user jacob
        login = self.client.login(username='jacob', password='top_secret')
        # access the profile of the user 'user'
        response = self.client.get(reverse('users:profile'), {'comment_author_id': self.user.id})
        # Check we got the profile of the user 'user'
        self.assertEqual(response.context['comment_author'], self.user)
        # Check that we got the comment of the user 'user'
        self.assertEqual(response.context['comments'][0].content, 'Hi I am user')

class SaveProductViewTest(TestCase):
    def setUp(self):
        # create a user
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )
        # Create a category
        Category.objects.create(name='category1')
        self.category_id = Category.objects.get(name='category1').id
        # Create a product
        Product.objects.create(name='product1', picture='picture', category_id=self.category_id)
        self.product = Product.objects.get(name='product1')
        # Create a substitute
        Substitute.objects.create(name='substitute1', picture='picture')
        self.substitute = Substitute.objects.get(name='substitute1')

    def test_save_product_redirect_if_not_logged_in(self):
        sub_id = Substitute.objects.get(name='substitute1').id
        response = self.client.get(reverse('users:save_product', args=(sub_id,)))
        # Check that the user is redirected to the log_in view with a 'next' parameter if he is not logged in
        self.assertRedirects(response, '/users/log_in/?next=/users/save_product/' + str(sub_id) +'/')

    def test_product_belong_to_a_user(self):
        user = User.objects.get(username='jacob')
        sub_id = self.substitute.id
        # Connect the user
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('users:save_product', args=(sub_id,)))
        # Select all the products the user saved
        substitute = user.user_substitute.all()
        # Check that the products the user saved is the product that we created
        self.assertEqual(substitute[0], self.substitute)
        # Check that the user is redirected to the list_saved_products view after the product is saved
        self.assertRedirects(response, '/users/list_saved_products/')


class ListSavedProductsViewTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )
        # Create a category
        Category.objects.create(name='category1')
        self.category_id = Category.objects.get(name='category1').id
        # Create a product
        Product.objects.create(name='product1', picture='picture', category_id=self.category_id)
        self.product = Product.objects.get(name='product1')
        # Create a substitute
        Substitute.objects.create(name='substitute1', picture='picture')
        self.substitute = Substitute.objects.get(name='substitute1')

    def test_list_saved_products_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('users:list_saved_products'))
        # Check that the user is redirected to the log_in view with a 'next' parameter if he is not logged in
        self.assertRedirects(response, '/users/log_in/?next=/users/list_saved_products/')

    def test_list_saved_products_return_all_products_user_saved(self):
        user = User.objects.get(username='jacob')
        # We save a product for a user
        self.substitute.user_sub.add(user)
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('users:list_saved_products'))
        # Check that the first element of the list of products the user saved is the product that we created
        self.assertEqual(response.context['substitutes'][0], self.substitute)
        

class EditProfileViewTest(TestCase):
    def setUp(self):
        self.jacob = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )
        self.user = User.objects.create_user(
            username='user', email='user@hotmail.com', password='top_secret'
        )
        self.edit_jacob = EditProfile.objects.create(user=self.jacob, about_me='My name is jacob')
        

    def test_edit_profile_returns_200(self):
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.get(reverse('users:edit_profile'))
        self.assertEqual(response.status_code, 200)

    def test_edit_profile_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('users:edit_profile'))
        self.assertRedirects(response, '/users/log_in/?next=/users/edit_profile/')

    def test_edit_profile_change_name_and_update_about_me_of_user(self):
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.post(reverse('users:edit_profile'), {
            'username': 'testuser1',
            'about_me': 'Now my name is testuser1, jacob is dead'
        })
        
        # Check that the username 'jacob' becomes 'testuser1'
        self.testuser1 = User.objects.filter(email='jacob@hotmail.com')[0]
        self.assertEqual(self.testuser1.username, 'testuser1')
        # Check that about_me of jacob's user becomes 'Now my name is testuser1, jacob is dead'
        self.assertEqual(EditProfile.objects.filter(user=self.testuser1)[0].about_me, 'Now my name is testuser1, jacob is dead')

    def test_edit_profile_create_about_me_of_user(self):
        # This user don't have 'about_me', so our view function create a new entry for this user 
        # (in the function we enter in the first else)
        login = self.client.login(username='user', password='top_secret')
        response = self.client.post(reverse('users:edit_profile'), {
            'username': 'user',
            'about_me': 'My name is user'
        })
        # Check that the username still unchanged
        self.user_unchanged = User.objects.filter(email='user@hotmail.com')[0]
        self.assertEqual(self.user_unchanged.username, 'user')
        # Check that about_me of the user 'user' was set 'My name is user'
        self.assertEqual(EditProfile.objects.filter(user=self.user_unchanged)[0].about_me, 'My name is user')