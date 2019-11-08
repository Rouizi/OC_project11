from django.test import TestCase
from django.urls import reverse
from catalog.models import Category, Product, Substitute


class IndexTest(TestCase):
    def test_index_returns_200(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)


class ListSubstituteTest(TestCase):
    def setUp(self):
        # Create a category
        Category.objects.create(name='category1')
        self.category_id = Category.objects.get(name='category1').id
        # Create a product
        Product.objects.create(name='product1', picture='picture', category_id=self.category_id)
        self.product = Product.objects.get(name='product1')
        # Create a substitute
        Substitute.objects.create(name='substitute1', picture='picture')
        self.substitute = Substitute.objects.get(name='substitute1')
        self.substitute.composition.add(self.product)

    def test_list_substitute(self):
        product_id = Product.objects.get(name='product1').id
        response = self.client.get(reverse('catalog:list_substitute', args=(product_id,)))
        substitutes = self.product.substitutes.all()
        # Check that we got a response 'success'
        self.assertEqual(response.status_code, 200)
        # Check that we got the substitute we created
        self.assertEqual(response.context['substitutes'][0], substitutes[0])

    def test_list_substitute_returns_404(self):
        product_id = Product.objects.get(name='product1').id + 1
        response = self.client.get(reverse('catalog:list_substitute', args=(product_id,)))
        self.assertEqual(response.status_code, 404)


class DetailSubstituteTest(TestCase):
    def setUp(self):
        c1 = Category.objects.create(name='category1')
        self.category_id = Category.objects.get(name='category1').id
        p1 = Product.objects.create(name='product1', picture='picture', category_id=self.category_id)
        self.product = Product.objects.get(name='product1')
        s1 = Substitute.objects.create(name='substitute1', picture='picture', nutri_score='A', nutrition='ingredients')

    def test_detail_substitute_returns_200(self):
        substitute_id = Substitute.objects.get(name='substitute1').id
        response = self.client.get(reverse('catalog:detail_substitute', args=(substitute_id,)))
        self.assertEqual(response.status_code, 200)

    def test_detail_substitute_returns_404(self):
        product_id = Product.objects.get(name='product1').id + 1
        response = self.client.get(reverse('catalog:detail_substitute', args=(product_id,)))
        self.assertEqual(response.status_code, 404)