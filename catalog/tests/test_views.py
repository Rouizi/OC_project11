from django.test import TestCase
from django.urls import reverse
from catalog.models import Category, Product, Substitute
from blog.models import Comment
from django.contrib.auth.models import User
import json


class IndexViewTest(TestCase):
    def test_index_returns_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'base.html')


class ListSubstituteViewTest(TestCase):
    def setUp(self):
        # Create a category
        self.category = Category.objects.create(name='category1')
        # Create a product
        self.product = Product.objects.create(name='product1', picture='picture', category_id=self.category.id)
        # Create a substitute
        self.substitute = Substitute.objects.create(name='substitute1', picture='picture')
        self.substitute.composition.add(self.product)

    def test_list_substitute(self):
        product_id = Product.objects.get(name='product1').id
        response = self.client.get(reverse('catalog:list_substitute', args=(product_id,)))
        substitutes = self.product.substitutes.all()
        # Check that we got a response 'success'
        self.assertEqual(response.status_code, 200)
        # Check that we got the substitute we created
        self.assertEqual(response.context['substitutes'][0], substitutes[0])
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/search.html')

    def test_list_substitute_returns_404(self):
        product_id = Product.objects.get(name='product1').id + 1
        response = self.client.get(reverse('catalog:list_substitute', args=(product_id,)))
        self.assertEqual(response.status_code, 404)


class DetailSubstituteViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='category1')
        self.product = Product.objects.create(name='product1', picture='picture', category_id=self.category.id)
        self.substitute = Substitute.objects.create(name='substitute1', picture='picture', nutri_score='A', nutrition='ingredients')
        self.user = User.objects.create_user(
            username='jacob', email='jacob@hotmail.com', password='top_secret'
        )

    def test_detail_substitute_returns_200(self):
        substitute_id = Substitute.objects.get(name='substitute1').id
        response = self.client.get(reverse('catalog:detail_substitute', args=(substitute_id,)))
        self.assertEqual(response.status_code, 200)
        self.assertEquals(response.context['substitute'].name, str(self.substitute))
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/detail_substitute.html')

    def test_detail_substitute_returns_404(self):
        product_id = Product.objects.get(name='product1').id + 1
        response = self.client.get(reverse('catalog:detail_substitute', args=(product_id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_substitute_returns_error_message_if_post_without_login(self):
        # Try to post message without login
        response = self.client.post(reverse('catalog:detail_substitute', args=(self.substitute.id,)),  {'content': 'good product'})
        messages = list(response.context['messages'])
        self.assertEquals(str(messages[0]), 'Vous devez vous connecter pour pouvoir poster un message!')

    def test_new_comment_is_registred(self):
        old_comments = Comment.objects.count() # count comments before a request
        login = self.client.login(username='jacob', password='top_secret')
        response = self.client.post(reverse('catalog:detail_substitute', args=(self.substitute.id,)),  {'content': 'good product'})
        new_comments = Comment.objects.count() # count comments after
        self.assertEquals(new_comments, old_comments + 1) # make sure 1 comment was added



class SearchViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='category1')
        self.product = {}
        for i in range(0, 10): # create 10 products for pagination
            self.product[i] = Product.objects.create(name=f'product{i}', barcode=f'{i}'*4, picture=f'picture{i}',
                                                     category_id=self.category.id)

    def test_auto_completion_system(self):
        response = self.client.get(reverse('catalog:search'),  {'content': 'test'})
        self.assertEquals(json.loads(response.content.decode('utf-8'))['status'], 'ZERO_RESULTS')
        # Here we have all the products because 'product' is contained in 'product1', 'product2' ...
        response = self.client.get(reverse('catalog:search'),  {'content': 'product'}) 
        for i in self.product.keys():
            self.assertEquals(json.loads(response.content.decode('utf-8'))['products'][i]['name'], self.product[i].name)


    def test_search_returns_200(self):
        # When the variable 'content' does not appear in the dictionary of the request, it means that the user has submitted his search
        response = self.client.get(reverse('catalog:search'),  {'query': '', 'page': 2}) # if query = '' we get all the products
        self.assertEquals(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/search.html')
        # Check that the second page contains 4 products (so the first contains 6 products)
        self.assertEquals(len(response.context['products']), 4)
        for i in range(4):
            self.assertEquals((response.context['products'][i]), self.product[i + 6]) # i + 6 because we are in the second page
        
        response = self.client.get(reverse('catalog:search'),  {'query': 'product1'})
        # Check that we have all the products whose names contain the content of the 'query' variable
        self.assertEquals(response.context['products'][0], self.product[1])
        response = self.client.get(reverse('catalog:search'),  {'query': '4444'})
        # Check that if no product was found by name we search by barcode
        self.assertEquals(response.context['products'][0], self.product[4])

    def test_pagination_returns_last_page_if_page_out_of_range(self):
        response = self.client.get(reverse('catalog:search'),  {'query': '',  'page': 999})
        # Check that if page is out of range (e.g. 999), deliver last page of results
        self.assertEquals(response.context['products'].number, 2)
        


class ListCategoriesViewTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='category1')

    def test_list_categories(self):
        response = self.client.get(reverse('catalog:list_categories'))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/list_categories.html')
        

class ListProductsViewTest(TestCase):
    def setUp(self):
        self.category1 = Category.objects.create(name='category1')
        self.category2 = Category.objects.create(name='category2')
        self.product_belong_category1 = {}
        for i in range(0, 50): # create 50 products that belongs to category1
            if i < 10: # The first 10 products have their nutri_score set to 'E'
                self.product_belong_category1[i] = Product.objects.create(name=f'product{i}', nutri_score='E', picture=f'picture{i}', category_id=self.category1.id)
            elif 10 <= i < 20:
                self.product_belong_category1[i] = Product.objects.create(name=f'product{i}', nutri_score='D', picture=f'picture{i}', category_id=self.category1.id)
            elif 20 <= i < 30:
                self.product_belong_category1[i] = Product.objects.create(name=f'product{i}', nutri_score='A', picture=f'picture{i}', category_id=self.category1.id)
            elif 30 <= i < 40:
                self.product_belong_category1[i] = Product.objects.create(name=f'product{i}', nutri_score='B', picture=f'picture{i}', category_id=self.category1.id)
            elif 40 <= i < 50:
                self.product_belong_category1[i] = Product.objects.create(name=f'product{i}', nutri_score='C', picture=f'picture{i}', category_id=self.category1.id)

        # for pagination we must have more than 50 products to have at least 2 pages since each page contains 50 products
        self.product_belong_category2 = {}
        for i in range(50, 53): # create 3 products that belongs to category2
            self.product_belong_category2[i] = Product.objects.create(name=f'product{i}', nutri_score='A', picture=f'picture{i}', category_id=self.category2.id)
        
        
    def test_list_products_returns_all_products_of_selected_category(self):
        response = self.client.get(reverse('catalog:list_products'), {'cat_id': self.category2.id})
        # Check that we have all products of category2 (only 3 products belongs to this category)
        self.assertEquals(len(response.context['products']), len(self.product_belong_category2.values()))
        # Check that all products we have are the same of products that belongs to category2
        for i in range(3):
            self.assertTrue(response.context['products'][i] == self.product_belong_category2[i + 50])

    def test_list_products_returns_all_products_of_all_categories(self):
        # If 'cat_id' is not in the request get then our function returns all products of all categories
        response = self.client.get(reverse('catalog:list_products'))
        self.assertEqual(response.status_code, 200)
        # Check we used correct template
        self.assertTemplateUsed(response, 'catalog/list_products.html')
        # Check that we have all products
        self.assertEquals(response.context['products'].paginator.count, 53)


    def test_pagination(self):
        response = self.client.get(reverse('catalog:list_products'))
        # Check that the first page contains 50 products
        self.assertEquals(len(response.context['products'].paginator.page(1)), 50)
        # Check that the second page contains 3 products
        self.assertEquals(len(response.context['products'].paginator.page(2)), 3)
        response = self.client.get(reverse('catalog:list_products'), {'page': 999})
        # Check that if page is out of range (e.g. 999), deliver last page of results
        self.assertEquals(response.context['products'].number, 2)
        # Same test with 'order_by' parameter
        response = self.client.get('http://127.0.0.1:8000/catalog/products/?page=999&order_by=nutri_score')
        self.assertEquals(response.context['products'].number, 2)

        

    def test_list_products_order_products_by_nutriscore_increasing(self):
        response = self.client.post(reverse('catalog:list_products'), {'select': 'nutri_score'})

        for i in range(50): # The first page
            if i < 13: # There are 10 products of category1 and 3 products of category2 which have their nutriscore equal to 'A'
                self.assertTrue(response.context['products'][i].nutri_score == 'A')
            elif 13 <= i < 23:
                self.assertTrue(response.context['products'][i].nutri_score == 'B')
            elif 23 <= i < 33:
                self.assertTrue(response.context['products'][i].nutri_score == 'C')
            elif 33 <= i < 43:
                self.assertTrue(response.context['products'][i].nutri_score == 'D')
            # There are 10 products which have their nutriscore equal to 'E', but we are in the first
            # page (50 products per page) so the other 3 products are in the 2 page
            elif 43 <= i < 50:                 
                self.assertTrue(response.context['products'][i].nutri_score == 'E')

        # Check if we request the second page, our products are still ordered 
        response = self.client.get('http://127.0.0.1:8000/catalog/products/?page=2&order_by=nutri_score&cat_id=0') 
        print(response.context['products'][0].nutri_score)
        for i in range(3):
            self.assertTrue(response.context['products'][i].nutri_score == 'E')