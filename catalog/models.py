from django.db import models
from django.core.files import File
from django.core.files.temp import NamedTemporaryFile
from .openfoodfacts import OpenFoodFacts
import requests
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    nutri_score = models.ImageField(upload_to="images/")
    barcode = models.CharField(max_length=30)
    picture = models.ImageField(upload_to="images/")
    # I made assumption that a product can belong to a single category so as not to complicate things
    category = models.ForeignKey('Category', on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Substitute(models.Model):
    name = models.CharField(max_length=255)
    nutri_score = models.ImageField(upload_to="images/")
    barcode = models.CharField(max_length=30)
    url = models.URLField()
    nutrition = models.ImageField(upload_to="images/")
    picture = models.ImageField(upload_to="images/")
    # A product can have several substitutes and a substitute can be the substitute for several products
    composition = models.ManyToManyField(Product, related_name="substitutes")
    user_sub = models.ManyToManyField(User, related_name='user_substitute')

    def __str__(self):
        return self.name


def save_image_from_url(field, url, image, i, save):
    """This function download an image from a given url"""

    r = requests.get(url)
    img_temp = NamedTemporaryFile(delete=True)
    img_temp.write(r.content)
    img_temp.flush()

    field.save(image + str(i) + url[-4:], File(img_temp), save=save)

# I executed this function during the development phase only once in the module views.py to fill the database. If it is executed
# in the module models.py django throws the exeption django.core.exceptions.AppRegistryNotReady: Models aren't loaded yet.
def insert_data_in_database():
    """This function records the data recover from openfoodfacts in the database of my site"""

    of = OpenFoodFacts('https://fr.openfoodfacts.org/categories&json=1', 'https://fr.openfoodfacts.org/api/v0/produit')
    dict_substitute, dict_cat_prod, list_of_categories = of.get_substitute()

    # recording of categories
    for category_name in list_of_categories:
        print(category_name)
        Category.objects.create(name=category_name)

    # recording of products
    i = 1
    for cat_name, dict_prod in dict_cat_prod.items():
        category = Category.objects.filter(name=cat_name)
        print("CATEGORY: ", category[0])
        for prod_name, values in dict_prod.items():
            p = Product()
            p.name = prod_name
            # values[0] is the nutriscore
            if values[0] == "A":
                p.nutri_score = 'images/nutriscore-a.svg'
            elif values[0] == "B":
                p.nutri_score = 'images/nutriscore-b.svg'
            elif values[0] == "C":
                p.nutri_score = 'images/nutriscore-c.svg'
            elif values[0] == "D":
                p.nutri_score = 'images/nutriscore-d.svg'
            elif values[0] == "E":
                p.nutri_score = 'images/nutriscore-e.svg'
            p.barcode = values[1] #values[1] is the barcode
            p.category = category[0]
            save_image_from_url(p.picture, values[2], "prod", i, True) # values[2] is the url of the image
            i += 1


    # recording of substitutes
    j = 1
    for sub_name, values in dict_substitute.items():
        s = Substitute()
        s.name = sub_name
        if values[0] == "A":
            s.nutri_score = 'images/nutriscore-a.svg'
        elif values[0] == "B":
            s.nutri_score = 'images/nutriscore-b.svg'
        elif values[0] == "C":
            s.nutri_score = 'images/nutriscore-c.svg'
        elif values[0] == "D":
            s.nutri_score = 'images/nutriscore-d.svg'
        elif values[0] == "E":
            s.nutri_score = 'images/nutriscore-e.svg'
        s.barcode = values[1]
        s.url = values[2]
        save_image_from_url(s.nutrition, values[3], "ing_subst", j, False)
        save_image_from_url(s.picture, values[4], "subst", j, True)
        j += 1
        for code in values[-1]: # values[-1] is a list that contains the barcode of products
            print(code)
            p = Product.objects.filter(barcode=code)
            print(p)
            print(p[0])
            s.composition.add(p[0])

