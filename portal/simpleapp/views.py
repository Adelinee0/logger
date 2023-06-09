from django.shortcuts import render
from datetime import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.generic import ListView, DetailView, DeleteView, CreateView, UpdateView
from .models import Post, Author
from .filters import PostFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from django.views.decorators.csrf import csrf_protect
from .models import Subscription, Category
from django.shortcuts import redirect, get_object_or_404
from django.core.cache import cache
from django.http import HttpResponse
from django.views import View
from .tasks import hello, printer


class PostList(ListView):
    model = Post
    ordering = '-createDate'
    template_name = 'posts.html'
    context_object_name = 'posts'
    paginate_by = 5


    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = PostFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)
        context['time_now'] = datetime.utcnow()
        context['filterset'] = self.filterset
        context['is_author'] = self.request.user.groups.filter(name='authors').exists()
        return context

class PostDetail(DetailView):
    model = Post
    template_name = 'post.html'
    context_object_name = 'post'

def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST)
        form.save()
        return HttpResponseRedirect('/posts')
    form = PostForm()
    return  render(request, 'post_edit.html', {'form': form})


def get_object(self, *args, **kwargs):
    obj = cache.get(f'post-{self.kwargs["pk"]}',
                    None)
    if not obj:
        obj = super().get_object(queryset=self.queryset)
        cache.set(f'post-{self.kwargs["pk"]}', obj)

    return obj

class NewsCreate(LoginRequiredMixin, CreateView, PermissionRequiredMixin):
    permission_required = ('simpleapp.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.categoryType = 'NW'
        post.author = self.request.user.author
        return super().form_valid(form)

class ArticleCreate(LoginRequiredMixin, CreateView,  PermissionRequiredMixin):
    permission_required = ('simpleapp.add_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        post.categoryType = 'AR'
        post.author = self.request.user.author
        return super().form_valid(form)

class NewsUpdate(LoginRequiredMixin, UpdateView,  PermissionRequiredMixin):
    permission_required = ('simpleapp.change_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

class ArticleUpdate(LoginRequiredMixin, UpdateView,  PermissionRequiredMixin):
    permission_required = ('simpleapp.change_post',)
    raise_exception = True
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

class NewsDelete(LoginRequiredMixin, DeleteView,  PermissionRequiredMixin):
    permission_required = ('simpleapp.delete_post',)
    raise_exception = True
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

class ArticleDelete(LoginRequiredMixin, DeleteView,  PermissionRequiredMixin):
    permission_required = ('simpleapp.delete_post',)
    raise_exception = True
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('post_list')

@login_required
@csrf_protect
def subscriptions(request):
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        category = Category.objects.get(id=category_id)
        action = request.POST.get('action')

        if action == 'subscribe':
            Subscription.objects.create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(
                user=request.user,
                category=category,
            ).delete()

    categories_with_subscriptions = Category.objects.annotate(
        user_subscribed=Exists(
            Subscription.objects.filter(
                user=request.user,
                category=OuterRef('pk'),
            )
        )
    ).order_by('name')
    return render(
        request,
        'subscriptions.html',
        {'categories': categories_with_subscriptions},
    )

class CategoryListView(ListView):
    model = Post
    template_name = 'category_list.html'
    context_object_name = 'category_news_list'

    def get_queryset(self):
        self.category = get_object_or_404(Category, id=self.kwargs['pk'])
        queryset =  Post.objects.filter(category=self.category).order_by('-createDate')
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_not_subscriber'] = self.request.user not in self.category.subscribers.all()
        context['category'] = self.category
        return context

@login_required
def subscribe(request, pk):
    user = request.user
    category = Category.objects.get(id=pk)
    category.subscribers.add(user)
    message = 'Вы успешно подписались на новоси категории'
    return  render(request, 'subscribe.html', {'category': category, 'message': message  })

class IndexView(View):
    def get(self, request):
        printer.delay(10)
        hello.delay()
        return HttpResponse('Hello!')

