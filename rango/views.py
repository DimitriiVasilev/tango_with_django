from django.shortcuts import render
from . models import Category, Page
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime

from .forms import CategoryForm, PageForm, UserProfileForm, UserForm


@login_required
def add_category(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            cat = form.save(commit=True)
            print(cat, cat.slug)
            return index(request)
        else:
            print(form.errors)
    else:
        form = CategoryForm()
    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    try:
        cat = Category.objects.get(slug=category_name_slug)
    except Category.DoesNotExist:
        cat = None

    if request.method == 'POST':
        form = PageForm(request.POST)
        if form.is_valid():
            page = form.save(commit=False)
            page.category = cat
            page.save()
            return show_category(request, category_name_slug)
        else:
            print(form.errors)
    else:
        form = PageForm()
    context_dic = {'form': form, 'category': cat}
    return render(request, 'rango/add_page.html', context_dic)


def index(request):
    categories_most_liked = Category.objects.order_by('-likes')[:5]
    pages_most_viewed = Page.objects.order_by('-views')[:5]
    context_dic = {
        'categories_most_liked': categories_most_liked,
        'pages_most_viewed': pages_most_viewed
    }

    visits = request.session.get('visits')
    if not visits:
        visits = 1

    last_visit = request.session.get('last_visit')
    if last_visit:
        last_visit_time = datetime.strptime(last_visit[:-7], "%Y-%m-%d %H:%M:%S")
        context_dic['last_visit'] = last_visit_time
        visits += 1

    request.session['last_visit'] = str(datetime.now())
    request.session['visits'] = visits
    context_dic['visits'] = visits

    return render(request, 'rango/index.html', context_dic)


def about(request):
    if request.session.get('visits'):
        visits = request.session.get('visits')
    else:
        visits = 1
    return render(request, "rango/about.html", {'visits': visits})


def show_category(request, category_name_slug):
    context_dic = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dic['pages'] = pages
        context_dic['category'] = category
    except Category.DoesNotExist:
        context_dic['pages'] = None
        context_dic['category'] = None
    context_dic['category_name_slug'] = category_name_slug
    return render(request, 'rango/category.html', context_dic)


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save(commit=False)
            user.set_password(user.password)
            user.save()

            profile = profile_form.save(commit=False)
            profile.user = user
            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']
            profile.save()

            registered = True
        else:
            print(user_form.errors, profile_form.errors)
    else:
        user_form = UserForm()
        profile_form = UserProfileForm()
    context_dic = {
        'user_form': user_form,
        'profile_form': profile_form,
        'registered': registered
    }
    return render(request, 'rango/register.html', context_dic)


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)
        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/rango/')
            else:
                return HttpResponse('Your Rango account is disabled.')
        else:
            print("Invalid login details: {0}, {1}".format(username, password))
            return HttpResponse('Invalid login details')
    else:
        return render(request, 'rango/login.html')


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect('/rango/')


@login_required
def restricted(request):
    return HttpResponse("since you're logging in, you are a good boy!")
