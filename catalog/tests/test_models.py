from django.test import TestCase
from catalog.models import Category, Product, Substitute


class CategoryModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='category1')

    def test_category_name(self):
        category = Category.objects.get(name='category1')
        expected_category_name = f'{self.category.name}'
        self.assertAlmostEqual(expected_category_name, str(category))


class ProductModelTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name='category1')
        self.product = Product.objects.create(name='product1', category_id=self.category.id)

    def test_product_name(self):
        product = Product.objects.get(name='product1')
        expected_product_name = f'{self.product.name}'
        self.assertAlmostEqual(expected_product_name, str(product))


class SubstituteModelTest(TestCase):
    def setUp(self):
        self.substitute = Substitute.objects.create(name='substitute1')

    def test_substitute_name(self):
        substitute = Substitute.objects.get(name='substitute1')
        expected_substitute_name = f'{self.substitute.name}'
        self.assertAlmostEqual(expected_substitute_name, str(substitute))