from django.views.generic import DetailView
from news.models import Post
from django.core.cache import cache


class PostDetail(DetailView):
    model = Post
    template_name = 'news_detail.html'
    context_object_name = 'post_detail'

    def get_object(self, queryset=None):
        cache_key = f'post-{self.kwargs["pk"]}'
        post = cache.get(cache_key)

        if not post:
            post = super().get_object(queryset=queryset)
            cache.set(cache_key, post)

        return post

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.get_object()
        context['post_type'] = post.post_type
        return context
