from django.test import TestCase
from catalog.openfoodfacts import OpenFoodFacts
import mock
from requests.models import Response


categories_name = ['conserves', 'confiseries', 'chocolats', 'biscuits fourrés', 'produits à tartiner', 'céréales et dérivés',
                      'desserts', 'surgelés', 'sauces', 'confitures et marmelades']
cat_json = {
    "count":16946,
    "tags":[]
}
for i in categories_name:
    data = dict()
    data['name'] = i
    cat_json['tags'].append(data)

cat_conserves_json = {
    "products": [],
}
cat_confiseries_json = {
    "products": [],
}
cat_chocolats_json = {
    "products": [],
}
cat_with_zero_prod_json = {
    "products": [{}],
}
for i in range(1, 21):
    data = dict()
    data['product_name'] = f"product{i}"
    data['nutrition_grade_fr'] = "C"
    data['code'] = str(i)
    data['image_front_url'] = f"url_prod{i}"
    cat_conserves_json['products'].append(data)
for i in range(21, 41):
    data = dict()
    data['product_name'] = f"product{i}"
    data['nutrition_grade_fr'] = "D"
    data['code'] = str(i)
    data['image_front_url'] = f"url_prod{i}"
    cat_confiseries_json['products'].append(data)
for i in range(41, 61):
    data = dict()
    data['product_name'] = f"product{i}"
    data['nutrition_grade_fr'] = "E"
    data['code'] = str(i)
    data['image_front_url'] = f"url_prod{i}"
    cat_chocolats_json['products'].append(data)


# requests.get('https://fr.openfoodfacts.org/api/v0/produit/4060800002242.json')
dict_prod1 = {'product':{'categories': 'cat11,cat12'}}
dict_prod2 = {'product':{'categories': 'cat21,cat22'}}
dict_prod3 = {'product':{'categories': 'cat11,cat22'}}
dict_prod = {'product':{'categories': 'cat11,cat22'}}
# requests.get('https://fr.openfoodfacts.org/categorie/boissons-sans-alcool/1.json')
dic_cat11_count = {'products': [], 'count': 50}
dic_cat21_count = {'products': [], 'count': 50}
dic_cat12_count = {'count': 125}
dic_cat22_count = {'count': 125}
for i in range(1, 8):
    data = dict()
    data['product_name'] = f"substitute{i}"
    data['nutrition_grade_fr'] = "A"
    data['code'] = str(i)
    data['url'] = "url"
    data['image_front_url'] = "image_front_url"
    data['image_nutrition_url'] = 'image_nutrition_url'
    dic_cat11_count['products'].append(data)
for i in range(7, 14):
    data = dict()
    data['product_name'] = f"substitute{i}"
    data['nutrition_grade_fr'] = "B"
    data['code'] = str(i)
    data['url'] = "url"
    data['image_front_url'] = "image_front_url"
    data['image_nutrition_url'] = 'image_nutrition_url'
    dic_cat21_count['products'].append(data)


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'https://fr.openfoodfacts.org/categories&json=1':
        return MockResponse(cat_json, 200)

    elif args[0] == 'https://fr.openfoodfacts.org/categorie/conserves/1.json':
        return MockResponse(cat_conserves_json, 200)
    elif args[0] == 'https://fr.openfoodfacts.org/categorie/confiseries/1.json':
        return MockResponse(cat_confiseries_json, 200)
    elif args[0] == 'https://fr.openfoodfacts.org/categorie/chocolats/1.json':
        return MockResponse(cat_chocolats_json, 200)


    elif args[0] == 'https://fr.openfoodfacts.org/api/v0/produit/1.json':
        return MockResponse(dict_prod1, 200)
    elif args[0] == 'https://fr.openfoodfacts.org/api/v0/produit/2.json':
        return MockResponse(dict_prod2, 200)
    elif args[0] == 'https://fr.openfoodfacts.org/api/v0/produit/3.json':
        return MockResponse(dict_prod3, 200)

    if args[0] == 'https://fr.openfoodfacts.org/categorie/cat11/1.json':
        return MockResponse(dic_cat11_count, 200)
    elif args[0] == 'https://fr.openfoodfacts.org/categorie/cat12/1.json':
        return MockResponse(dic_cat12_count, 200)
    elif args[0] == 'https://fr.openfoodfacts.org/categorie/cat21/1.json':
        return MockResponse(dic_cat21_count, 200)
    elif args[0] == 'https://fr.openfoodfacts.org/categorie/cat22/1.json':
        return MockResponse(dic_cat22_count, 200)
    for i in range(20):
        if args[0] == 'https://fr.openfoodfacts.org/categorie/cat/' + str(i) + '.json':
            return MockResponse({'products': [], 'count': 256}, 200)

    for i in range(10):
        for page in range(1, 20):
            if args[0] == 'https://fr.openfoodfacts.org/categorie/' + categories_name[i] + '/' + str(page) + '.json':
                # We test the method get_product for only 3 category
                if i > 2:
                    return MockResponse(cat_with_zero_prod_json, 200)
                # and only for the first page
                if page > 1:
                    return MockResponse(cat_with_zero_prod_json, 200)

    for i in range(1, 61):
        if i > 3:
            if args[0] == 'https://fr.openfoodfacts.org/api/v0/produit/' + str(i) + '.json':
                return MockResponse({f'product':{'categories': 'cat'}}, 200)




class OpenFoodFactsTest(TestCase):
    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_category(self, mock_get):
        # Assert requests.get calls
        of = OpenFoodFacts('https://fr.openfoodfacts.org/categories&json=1', None)
        list_of_categories = of.get_category()
        self.assertEqual(list_of_categories, ['conserves', 'confiseries', 'chocolats', 'biscuits fourrés', 'produits à tartiner',
                                              'céréales et dérivés','desserts', 'surgelés', 'sauces', 'confitures et marmelades'])

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_product(self, mock_get):
        of = OpenFoodFacts('https://fr.openfoodfacts.org/categories&json=1', None)
        dict_cat_prod, list_of_categories = of.get_product()

        cat = [cat_conserves_json, cat_confiseries_json, cat_chocolats_json]
        dict_test = {}
        for i in range(3):
            dict_prod = {}
            for l in cat[i].values(): # l is a list
                for prod_detail in l:
                    dict_prod[prod_detail['product_name']] = [prod_detail['nutrition_grade_fr'], prod_detail['code'], prod_detail['image_front_url']]
                dict_test[categories_name[i]] = dict_prod
        for i in range(3, 10):
                dict_test[categories_name[i]] = {}

        self.assertEqual(dict_cat_prod, dict_test)

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_get_substitute(self, mock_get):
        of = OpenFoodFacts('https://fr.openfoodfacts.org/categories&json=1', 'https://fr.openfoodfacts.org/api/v0/produit')
        dict_substitute, dict_cat_prod, list_of_categories = of.get_substitute()
        dict_test = {}
        for i in range(1, 7):
            dict_test[f'substitute{i}'] = ['A', f'{i}', 'url', 'image_nutrition_url', 'image_front_url', ['1', '3']]
        for i in range(7, 13):
            dict_test[f'substitute{i}'] = ['B', f'{i}', 'url', 'image_nutrition_url', 'image_front_url', ['2']]
        self.assertEqual(dict_substitute, dict_test)