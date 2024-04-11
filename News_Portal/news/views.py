from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from .models import Post, Subscription, Category
from .filters import NewsFilter
from .forms import PostForm
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest
from django.contrib.auth.mixins import PermissionRequiredMixin
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef



class PostList(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'news.html'
    context_object_name = 'post'
    paginate_by = 3


class PostDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'post_detail'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.get_object()
        post_type = post.post_type

        context['post_type'] = post_type

        return context


class PostSearch(ListView):
    model = Post
    ordering = '-published'
    template_name = 'news_search.html'
    context_object_name = 'post_search'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        if self.request.GET:  # Проверка наличия данных в GET
            return self.filterset.qs
        else:
            return Post.objects.none()  # Возвращаем пустой queryset, если нет данных в GET

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['total_post_search_count'] = self.filterset.qs.count()
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
        # Устанавливаем тип записи в зависимости от URL
        if 'news' in self.request.path:
            post.post_type = 'news'
        elif 'articles' in self.request.path:
            post.post_type = 'article'

        post.save()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        object_type = 'Добавить новость' if 'news' in self.request.path else 'Добавить статью'
        context['object_type'] = object_type

        return context


class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        post = self.get_object()
        if 'news' in self.request.path and post.post_type != 'news':
            context['error_message'] = "Вы пытаетесь изменить статью как новость"
        elif 'articles' in self.request.path and post.post_type != 'article':
            context['error_message'] = "Вы пытаетесь изменить новость как статью"

        object_type = 'Изменить новость' if 'news' in self.request.path else 'Изменить статью'
        context['object_type'] = object_type

        return context


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post', )
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        if 'news' in self.request.path and post.post_type != 'news':
            context['error_message'] = "Вы пытаетесь удалить статью как новость"
        elif 'articles' in self.request.path and post.post_type != 'article':
            context['error_message'] = "Вы пытаетесь удалить новость как статью"

        object_type = 'Удалить новость' if 'news' in self.request.path else 'Удалить статью'
        context['object_type'] = object_type

        return context

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        if 'error_message' in self.get_context_data():
            return HttpResponseBadRequest("Ошибка: {}".format(self.get_context_data()['error_message']))
        return super().delete(request, *args, **kwargs)


@login_required
@csrf_protect
def subscription_view(request):
    # Выбираем только те категории, которые имеют посты
    categories_with_posts = Category.objects.filter(
        post__isnull=False
    ).distinct().annotate(
        is_subscribed=Exists(
            Subscription.objects.filter(user=request.user, category=OuterRef('pk'))
        )
    ).order_by('name')

    # Обрабатываем подписку/отписку
    if request.method == 'POST':
        category_id = request.POST.get('category_id')
        action = request.POST.get('action')
        category = get_object_or_404(Category, id=category_id)
        if action == 'subscribe':
            Subscription.objects.get_or_create(user=request.user, category=category)
        elif action == 'unsubscribe':
            Subscription.objects.filter(user=request.user, category=category).delete()
        return redirect('subscription_view')

    return render(request, 'subscriptions.html', {'categories': categories_with_posts})
