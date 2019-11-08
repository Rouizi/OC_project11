from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from catalog.models import Category, Product, Substitute


class SignUpTest(TestCase):
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


class LoginTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_login_user(self):
        response = self.client.post(reverse('users:log_in'), {'username': 'jacob', 'password': 'top_secret'}, follow=True)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'jacob')
        # Check that the user is redirected if the connection is successful
        self.assertRedirects(response, reverse('index'))


class LogoutTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_logout_user(self):
        response = self.client.get(reverse('users:log_out'), follow=True)
        # Check our user is logged in
        self.assertEqual(str(response.context['user']), 'AnonymousUser')
        # Check that the user is redirected to the log_in view if the logout is successful
        self.assertRedirects(response, reverse('users:log_in'))

class ProfileTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

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



class SaveProductTest(TestCase):
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


class ListSavedProductsTest(TestCase):
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

