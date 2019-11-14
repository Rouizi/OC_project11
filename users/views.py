from django.contrib.auth import login, authenticate, logout
from users.forms import SignUpForm, ConnexionForm, EditProfileForm
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from catalog.models import Substitute
from users.models import EditProfile



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
    title = 'Profile'

    current_user_id = request.user.id
    current_user = get_object_or_404(User, id=current_user_id)
    if 'comment_author_id' in request.GET:
        comment_author_id = request.GET['comment_author_id'] 
        comment_author = get_object_or_404(User, id=comment_author_id)
        edits = EditProfile.objects.filter(user=comment_author)
    else:
        edits = EditProfile.objects.filter(user=current_user)
  
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


@login_required
def edit_profile(request):
    title = 'Editer le profile'

    if request.method == "POST":
        # request.user.username is the original username
        form = EditProfileForm(request.user.username, request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            about_me = form.cleaned_data["about_me"]
            user = get_object_or_404(User, id=request.user.id)

            edit = EditProfile.objects.filter(user=user)
            if edit.exists():
                edit.update(about_me=about_me, user=user)
                user.username = username
                user.save()
            else:
                edit = EditProfile(about_me=about_me, user=user)
                user.username = username
                edit.save()
                user.save()
            messages.add_message(request, messages.SUCCESS,
                                     'Vos changements ont été enregistrés.')
            return redirect(reverse('users:profile'))
    else:
        edit = EditProfile.objects.filter(user=request.user)
        about_me = edit[0].about_me if edit.exists() else 'Décrivez vous en quelques mots'

        form = EditProfileForm(request.user.username,
                               {'username': request.user.username,
                                'about_me': about_me})
    return render(request, 'users/edit_profile.html', {'form': form ,'title': title})





