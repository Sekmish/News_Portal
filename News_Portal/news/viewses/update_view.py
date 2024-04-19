from django.views.generic import UpdateView
from django.contrib.auth.mixins import PermissionRequiredMixin
from news.models import Post
from news.forms import PostForm



class PostUpdate(PermissionRequiredMixin, UpdateView):
    permission_required = ('news.change_post', )
    form_class = PostForm
    model = Post
    template_name = 'post_edit.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
        if 'news' in self.request.path and post.post_type != 'news':
            context['error_message'] = "Вы пытаетесь изменить статью как новость"
        elif 'articles' in self.request.path and post.post_type != 'article':
            context['error_message'] = "Вы пытаетесь изменить новость как статью"
        object_type = 'Изменить новость' if 'news' in self.request.path else 'Изменить статью'
        context['object_type'] = object_type
        return context