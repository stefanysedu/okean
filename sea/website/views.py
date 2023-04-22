from django.contrib.auth import logout, login
from django.contrib.auth.views import LoginView
from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import HttpResponse, HttpResponseNotFound, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import *
from .models import *
from .utils import *


class Home(DataMixin, ListView):
    paginate_by = 4 # рыб на странице
    model = Fish
    template_name = 'fish/index.html'
    context_object_name = 'posts'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Главная страница")
        return dict(list(context.items()) + list(c_def.items()))

    def get_queryset(self):
        return Fish.objects.filter(is_published=True)


def about(request):
    contact_list = Fish.objects.all()
    paginator = Paginator(contact_list, 3)

    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return render(request, 'fish/about.html', {'page_obj': page_obj, 'menu': menu, 'title': 'Добро пожаловать на сайт Океанариума'})


class AddPage(LoginRequiredMixin, DataMixin, CreateView):
    form_class = AddPostForm
    template_name = 'fish/addpage.html'
    success_url = reverse_lazy('home')
    login_url = reverse_lazy('home')
    raise_exception = True

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Добавление обитателя")
        return dict(list(context.items()) + list(c_def.items()))


def contact(request):
    return render(request, 'fish/comments.html',{ 'menu': menu, 'title': 'Отзывы'})


def pageNotFound(request, exception):
    return HttpResponseNotFound('<h1>Страница не найдена</h1>')


class ShowPost(DataMixin, DetailView):
    model = Fish
    template_name = 'fish/post.html'
    slug_url_kwarg = 'post_slug'
    context_object_name = 'post'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title=context['post'])
        return dict(list(context.items()) + list(c_def.items()))


class Expose(DataMixin, ListView):
    model = Fish
    template_name = 'fish/index.html'
    context_object_name = 'posts'
    allow_empty = False

    def get_queryset(self):
        return Fish.objects.filter(cat__slug=self.kwargs['cat_slug'], is_published=True)

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title='Экспозиция - ' + str(context['posts'][0].cat),
                                      cat_selected=context['posts'][0].cat_id)
        return dict(list(context.items()) + list(c_def.items()))


class RegisterUser(DataMixin, CreateView):
    form_class = RegisterUserForm
    template_name = 'fish/register.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Регистрация")
        return dict(list(context.items()) + list(c_def.items()))

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect('home')

class LoginUser(DataMixin, LoginView):
    form_class = LoginUserForm
    template_name = 'fish/login.html'

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        c_def = self.get_user_context(title="Авторизация")
        return dict(list(context.items()) + list(c_def.items()))

    def get_success_url(self): # без этого будет перенаправление в ЛК
        return reverse_lazy('home')


def logout_user(request):
    logout(request)
    return redirect('login')