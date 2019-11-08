from django.shortcuts import render, get_object_or_404
from catalog.models import Product, Substitute



def index(request):
    title = 'Accueil'
    description = 'Pur Beurre est un site web d\'une jeune startup fondée par Remy et Colette Tatou, ' \
                  'deux restaurateurs de renom.'
    return render(request, 'base.html', {'title': title, 'description': description})


def list_substitute(request, product_id):
    id = int(product_id)
    product = get_object_or_404(Product, id=id)
    substitutes = product.substitutes.all()

    title = "Liste de substituts"
    message = "Substituts pour le produit : %s" %product.name

    return render(request, 'catalog/search.html',
                  {'substitutes': substitutes, 'title': title,
                   'message': message, 'product': product})


def detail_substitute(request, substitute_id):
    id = int(substitute_id)
    substitute = get_object_or_404(Substitute, id=id)
    title = "%s" %substitute.name

    return render(request, 'catalog/detail_substitute.html', {'substitute': substitute, 'title': title})


def search(request):
    query = request.GET['query']
    if not query:
        products = Product.objects.all()[:6]
    else:
        products = Product.objects.filter(name__icontains=query)[:6]

    if not products.exists():
        products = Product.objects.filter(barcode=query)

    title = "Liste de produits"
    message = "Résultats pour la recherche : %s" %query

    return render(request, 'catalog/search.html',
                  {'products': products, 'title': title, 'message': message, 'query': query})


def legal(request):
    title = 'Mentions légales'
    return render(request, 'catalog/legal.html', locals())