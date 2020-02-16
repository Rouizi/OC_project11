from django.shortcuts import render, get_object_or_404, redirect
from catalog.models import Category, Product, Substitute
from django.core.paginator import Paginator, EmptyPage
from catalog.forms import OptionForm
from blog.models import Comment
from blog.forms import CommentForm
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse



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
    message = "Substitut(s) pour le produit : %s" %product.name

    return render(request, 'catalog/search.html',
                  {'substitutes': substitutes, 'title': title,
                   'message': message, 'product': product})


@transaction.atomic
def detail_substitute(request, substitute_id):
    id = int(substitute_id)
    substitute = get_object_or_404(Substitute, id=id)
    title = "%s" %substitute.name
    comments = Comment.objects.filter(substitute=id).order_by('-date_added')
    
    if request.method == 'POST':
        if request.user.is_anonymous:
            messages.add_message(request, messages.ERROR,
                                 'Vous devez vous connecter pour pouvoir poster un message!')
            form = CommentForm()
            return render(request, 'catalog/detail_substitute.html', 
                    {'substitute': substitute, 'title': title, 'form': form, 'comments': comments}) 
        form = CommentForm(request.POST)
        if form.is_valid():
            # We use a transaction so that if one of the requests below fails all previous ones are canceled
            with transaction.atomic():
                comment = form.save(commit=False)
                user = User.objects.filter(id=request.user.id)
                comment.author = user[0]
                comment.substitute = substitute
                comment.save()
                form = CommentForm()
    else:
        form = CommentForm()

    return render(request, 'catalog/detail_substitute.html', 
                    {'substitute': substitute, 'title': title, 'form': form, 'comments': comments})


def search(request):
    title = "Liste des produits"
    if 'query' in request.GET:
        query = request.GET['query']
    # Auto-completion system with AJAX
    if 'content' in request.GET:
        content = request.GET.get('content', None)
        products = Product.objects.filter(name__icontains=content)[0:10].values()
        # We have to return somthing even if no result has been found so that the function break
        if not products.exists():
            return JsonResponse({'status': 'ZERO_RESULTS'})
        else:
            return JsonResponse({'status': 'ok', "products": list(products)})
    
    if not query:
        products = Product.objects.all().order_by('name')
    else:
        products = Product.objects.filter(name__icontains=query).order_by('name')

    if not products.exists():
        products = Product.objects.filter(barcode=query).order_by('name')

    paginator = Paginator(products, 6) # 6 products per page
    if 'page' in request.GET:
        page = request.GET['page']
    else:
        page = 1

    try:
        prods = paginator.page(page)
    except EmptyPage:
        # We return the last page
        prods = paginator.page(paginator.num_pages)

    message = "Résultat(s) pour la recherche : %s" %query

    return render(request, 'catalog/search.html',
                  {'products': prods, 'title': title, 'message': message, 'query': query})


def legal(request):
    title = 'Mentions légales'
    return render(request, 'catalog/legal.html', locals())


def list_categories(request):
    title = 'Liste des catégories'
    categories = Category.objects.all().order_by('id')

    return render(request, 'catalog/list_categories.html', {'title': title, 'categories': categories})


def list_products(request):
    title = 'Liste des produits'
    # cat_id == 0 when user want to display all products
    cat_id = request.GET['cat_id'] if 'cat_id' in request.GET else 0

    cat_id = int(cat_id)
    products = Product.objects.all().order_by('name') if cat_id == 0 else \
               Product.objects.filter(category_id=cat_id).order_by('name')

    paginator = Paginator(products, 50)  # 50 products per page
    page = request.GET['page'] if 'page' in request.GET else 1

    try:
        prods = paginator.page(page)
    except EmptyPage:
        # We return the last page
        prods = paginator.page(paginator.num_pages)

    if request.method == 'POST':
        form = OptionForm(request.POST)
        if form.is_valid():
            order_by = form.cleaned_data.get('select')
            products = Product.objects.all().order_by(order_by) if cat_id == 0 else \
                       Product.objects.filter(category_id=cat_id).order_by(order_by)
            paginator = Paginator(products, 50)
            try:
                prods = paginator.page(page)
            except EmptyPage:
                prods = paginator.page(paginator.num_pages)
            return render(request, 'catalog/list_products.html',
                          {'title': title, 'products': prods, 'form': form, 'order_by': order_by, 'cat_id': cat_id})
    elif 'order_by' in request.GET:
        order_by = request.GET['order_by']
        products = Product.objects.all().order_by(order_by) if cat_id == 0 else \
                   Product.objects.filter(category_id=cat_id).order_by(order_by)
        paginator = Paginator(products, 50)
        try:
            prods = paginator.page(page)
        except EmptyPage:
            prods = paginator.page(paginator.num_pages)
        form = OptionForm(initial={'select': order_by})
        return render(request, 'catalog/list_products.html',
                      {'title': title, 'products': prods, 'form': form, 'order_by': order_by, 'cat_id': cat_id})
    else:
        form = OptionForm()

    return render(request, 'catalog/list_products.html',
                  {'title': title, 'products': prods, 'form': form, 'cat_id': cat_id})

