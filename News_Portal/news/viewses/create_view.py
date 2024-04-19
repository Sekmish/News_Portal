from django.views.generic import CreateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from news.models import Post
from news.forms import PostForm



class PostCreate(PermissionRequiredMixin, CreateView):
    permission_required = ('news.add_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def form_valid(self, form):
        post = form.save(commit=False)
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