from django.contrib.auth import login, authenticate, logout
from users.forms import SignUpForm, ConnexionForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from catalog.models import Substitute



def signup(request):
    title = 'Inscription'

    if request.user.is_authenticated:
        return redirect('index')
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.add_message(request, messages.SUCCESS,
                                 'Félicitations, vous étes maintenant un utilisateur enregistré!')
            return redirect('index')
    else:
        form = SignUpForm()
    return render(request, 'users/signup.html', {'form': form ,'title': title})


def log_in(request):
    title = 'Connexion'
    error = False
    next = request.GET.get('next')
    if request.user.is_authenticated:
        return redirect('index')
    if request.method == "POST":
        form = ConnexionForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            user = authenticate(username=username, password=password)  # We check if the data is correct
            if user and next is None:  # If the returned object is not None
                login(request, user)  # we connect the user
                messages.add_message(request, messages.SUCCESS,
                                     f'Vous êtes connecté {username}')
                return redirect('index')
            elif user and next is not None:
                login(request, user)
                return redirect(next)
            else: # otherwise an error will be displayed
                error = True
    else:
        form = ConnexionForm()

    return render(request, 'users/login.html', locals())


def log_out(request):
    logout(request)
    return redirect(reverse('users:log_in'))


@login_required
def profile(request):
    title = 'Profil'
    id = request.user.id
    user = get_object_or_404(User, id=id)
    return render(request, 'users/profile.html', locals())


@login_required
def save_product(request, sub_id):
    user_id = request.user.id
    sub_id = int(sub_id)
    user = User.objects.filter(id=user_id)
    substitute = get_object_or_404(Substitute, id=sub_id)
    substitute.user_sub.add(user[0])

    return redirect('users:list_saved_products')


@login_required
def list_saved_products(request):
    title = 'Liste des produits sauvegarder'
    user_id = request.user.id
    user = User.objects.filter(id=user_id)
    # We select, since the relationship manytomany, all the substitutes that the user has saved
    substitutes = user[0].user_substitute.all()
    return render(request, 'users/list_saved_products.html', {'substitutes': substitutes, 'title': title})





