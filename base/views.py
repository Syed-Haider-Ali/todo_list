from django.forms.models import BaseModelForm
# from django.http import HttpResponse
from django.shortcuts import render, redirect
# from django.http import HttpResponse - not required in class based views
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy

from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin # to show data to only logged in user
# for LoginRequiredmixin - > LOGIN_URL = 'login' - ad login url in above static_url in settings
from django.contrib.auth.forms import UserCreationForm
# importing form for user registration instead of making from scratch
from django.contrib.auth import login #if a user get registered, it will be directly logged in
from .models import Task

# def taskList(request):
#     return HttpResponse('Todo List')

class RegisterPage(FormView):
    template_name = 'base/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True  # if user is authenticated redirect
    success_url = reverse_lazy('tasks') # if user gets signed up, it will be redirected to taskkList

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)
    
    def get(self, *args, **kwargs):  # if a user is logged in, it will not allow it to see login/register page
        if self.request.user.is_authenticated:
            return redirect('tasks')
        return super(RegisterPage, self).get(*args, **kwargs)


class CustomLoginView(LoginView):
    fields = '__all__'
    template_name = 'base/login.html'

    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('tasks')


class TaskList(LoginRequiredMixin,ListView):
    # it looks for task_list.html file automatically
    # it always requres a model 
    model = Task
    # it by default objects_list passes a dictionery passed to task_list.html, but to change object_list ->
    context_object_name = 'tasks'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].filter(user=self.request.user)
        context['count'] = context['tasks'].filter(complete=False).count()
        search_input = self.request.GET.get('search-area') or ''  # if not comming any query than None
        if search_input:
            context['tasks'] = context['tasks'].filter(title__startswith=search_input)
        context['search_input'] = search_input  # to keep search term in textbox
        return context


class TaskDetail(LoginRequiredMixin,DetailView):
    model = Task
    # by default dictionery name will be 'object' -> beauty of django
    context_object_name = 'task'
    # to modify template name
    template_name = 'base/task.html'


class TaskCreate(LoginRequiredMixin,CreateView):
    model = Task
    fields = ['title', 'description', 'complete']
    # or fields = ['title', etc]
    success_url = reverse_lazy('tasks')

    def form_valid(self, form): # editing default function
        form.instance.user = self.request.user
        return super(TaskCreate, self).form_valid(form)


class TaskUpdate(LoginRequiredMixin,UpdateView):
    model = Task
    fields = ['title', 'description', 'complete']
    success_url = reverse_lazy('tasks')


class TaskDelete(LoginRequiredMixin,DeleteView):
    model = Task
    context_object_name = 'task'
    success_url = reverse_lazy('tasks')

