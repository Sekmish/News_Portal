from django.views.generic import ListView
from news.models import Post
from news.filters import NewsFilter


class PostList(ListView):
    model = Post
    ordering = '-pk'
    template_name = 'news.html'
    context_object_name = 'post'
    paginate_by = 3


class PostSearchList(ListView):
    model = Post
    ordering = '-published'
    template_name = 'news_search.html'
    context_object_name = 'post_search'
    paginate_by = 5

    def get_queryset(self):
        queryset = super().get_queryset()
        self.filterset = NewsFilter(self.request.GET, queryset)
        return self.filterset.qs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filterset'] = self.filterset
        context['total_post_search_count'] = self.filterset.qs.count()
        return context
