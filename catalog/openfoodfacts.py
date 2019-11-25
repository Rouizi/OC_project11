import requests


"""This script will be executed once, its role is to retrieve data from openfoodfacts website"""

class OpenFoodFacts:
    """This class retrieves data from the web site OpenFoodFacts"""

    def __init__(self, url_cat, url_prod):
        self.url_cat = url_cat
        self.url_prod = url_prod


    def get_category(self):
        """This fonction retrives 10 categories from the web site"""

        r = requests.get(self.url_cat)  # self.url_cat = 'https://fr.openfoodfacts.org/categories&json=1'
        r_json = r.json()  # type(r_json) = dict
        data_categories = r_json['tags']  # type(data_category) = list

        list_of_categories = []
        # We want to have this category in list_of_category
        categories = ['confiseries', 'biscuits fourrés', 'produits à tartiner', 'céréales et dérivés',
                      'desserts', 'surgelés', 'sauces', 'conserves', 'chocolats', 'confitures et marmelades']

        for data_category in data_categories:  # type(data_category) = dict
            if data_category['name'].lower() in categories:
                list_of_categories.append(data_category['name'].lower())
        return list_of_categories

    def get_product(self):
        """This fonction retrives 50 products from each categories"""

        # We want to have products that belong to these categories
        list_of_categories = self.get_category()
        list_of_name_prod = []
        dict_cat_prod = {}
        # We go through each category
        for i in range(10):
            # We go through each page (20 pages max.) of each category. Actually we need only 3 pages to have our
            # 50 products but do not forget that some pages does not contain nutri_score or product_name in their fields
            for page in range(1, 20):
                # exemple: requests.get('https://fr.openfoodfacts.org/categorie/Confiseries/1.json')
                r = requests.get(self.url_cat[0:-8] + '/' + list_of_categories[i] + '/' + str(page) + '.json')
                r_json = r.json()
                data_products = r_json['products']  # type(data_products) = list
                dict_prod = {}
                for prod_detail in data_products:  # type(prod_detail) = dict
                    # According to the API of the web site some product may not have
                    # 'product_name', 'nutrition_grade_fr' or 'code' in their fiels so we make an if to filter all that
                    if ('product_name' in prod_detail and prod_detail['product_name'] != '' and
                        'nutrition_grade_fr' in prod_detail and prod_detail['nutrition_grade_fr'] != '' and
                        'code' in prod_detail and prod_detail['code'] != '' and
                        'image_front_url' in prod_detail and prod_detail['image_front_url'] != '' and
                        prod_detail['product_name'].lower() not in list_of_name_prod):
                        list_of_name_prod.append(prod_detail['product_name'].lower())
                        dict_prod[prod_detail['product_name']] = [prod_detail['nutrition_grade_fr'].upper(),
                                                                  prod_detail['code'], prod_detail['image_front_url']]


                # If dictionary is empty we can't do dict[x].update(dict2) so we enter in the first case
                if list_of_categories[i] not in dict_cat_prod:
                    dict_cat_prod[list_of_categories[i]] = dict_prod
                else:
                    dict_cat_prod[list_of_categories[i]].update(dict_prod)
                if len(dict_cat_prod[list_of_categories[i]]) > 50:
                    # We take only 50 products per category
                    dict_cat_prod[list_of_categories[i]] = dict(list(dict_cat_prod[list_of_categories[i]].items())[0:50])
                    break
        return dict_cat_prod, list_of_categories

    def get_substitute(self):
        """This fonction retrives a substitute for a given product"""

        dict_nutri_score = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
        dict_substitute = {}
        barcode_substitute = []
        dict_cat_prod, list_of_categories = self.get_product()
        id_product = 0
        for prod in dict_cat_prod.values(): # type(prod) = dict
            for prod_details in prod.values(): # type(prod_details) = list
                id_product += 1
                #print('id_product: ', id_product)
                # for exemple: r_prod = requests.get('https://fr.openfoodfacts.org/api/v0/produit/4060800002242.json')
                # prod_details is a list that contains the nutri_score, the barcode and the url of the product image
                r_prod = requests.get(self.url_prod + '/' + prod_details[1] + '.json')
                r_prod_json = r_prod.json()
                data_prod = r_prod_json['product'] # type(data_prod) = dict

                categories = data_prod['categories'].split(',')
                dict_categories = {}
                for name_cat in categories:
                    # exemple: requests.get('https://fr.openfoodfacts.org/categorie/boissons-sans-alcool/1.json')
                    r_cat = requests.get(self.url_cat[0:-8] + '/' + name_cat + '/1.json')
                    r_cat_json = r_cat.json()
                    nb_prod = r_cat_json['count']
                    dict_categories[nb_prod] = name_cat
                min_nb_prod = min(dict_categories.keys())
                cat_with_min_prod = dict_categories[min_nb_prod]
                # We search on the category that contains the least products to find a product that could be considered
                # as a substitute and we research on only 20 pages so as not to take too much time to find 6 substitutes
                nb_substitute = 0
                page_substitute = []
                for i in range(1, 20):
                    #print('page: ', i)
                    if nb_substitute > 6:
                        break
                    # exemple: requests.get('https://fr.openfoodfacts.org/categorie/Barres chocolatées/1.json')
                    r = requests.get(self.url_cat[0:-8] + '/' + cat_with_min_prod + '/' + str(i) + '.json')
                    r_json = r.json()
                    data_substitutes = r_json['products']
                    # If the category contains less then 20 pages ( ex: 6p), so beyond the 6th pages data_products = []
                    if not data_substitutes:
                        break

                    for subst_details in data_substitutes:

                        if 'nutrition_grade_fr' in subst_details and subst_details['nutrition_grade_fr'] != '':

                            # If the nutri_score of the substitute is better than that of the product so we take this substitute
                            # prod_details[0] is the nutri_score of the product
                            if dict_nutri_score[subst_details['nutrition_grade_fr'].lower()] < dict_nutri_score[prod_details[0].lower()]:
                                nb_substitute += 1
                                if nb_substitute > 6:
                                    break
                                if subst_details['code'] not in page_substitute:
                                    page_substitute.append(subst_details['code'])
                                else:
                                    continue
                                if ('product_name' in subst_details and subst_details['product_name'] != '' and
                                    'code' in subst_details and subst_details['code'] != '' and
                                    'url' in subst_details and subst_details['url'] != '' and
                                    'image_nutrition_url' in subst_details and subst_details['image_nutrition_url'] != '' and
                                    'image_front_url' in subst_details and subst_details['image_front_url'] != ''):

                                        if subst_details['code'] not in barcode_substitute:
                                            barcode_substitute.append(subst_details['code'])

                                            dict_substitute[subst_details['product_name'].lower()] = [
                                                subst_details['nutrition_grade_fr'].upper(),
                                                subst_details['code'],
                                                subst_details['url'],
                                                subst_details['image_nutrition_url'],
                                                subst_details['image_front_url'],
                                                [prod_details[1]]
                                            ]

                                        else:
                                            dict_substitute[subst_details['product_name'].lower()][-1].append(prod_details[1])

                                        #print(subst_details['product_name'])
                #print(dict_substitute)

        #print(list_of_categories)
        #print(dict_cat_prod)
        #print(dict_substitute)
        return dict_substitute, dict_cat_prod, list_of_categories


#of = OpenFoodFacts('https://fr.openfoodfacts.org/categories&json=1', 'https://fr.openfoodfacts.org/api/v0/produit')
#of.get_substitute()