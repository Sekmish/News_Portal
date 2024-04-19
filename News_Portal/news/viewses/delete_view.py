from django.views.generic import DeleteView
from django.urls import reverse_lazy
from django.http import HttpResponseBadRequest
from django.contrib.auth.mixins import PermissionRequiredMixin
from news.models import Post


class PostDelete(PermissionRequiredMixin, DeleteView):
    permission_required = ('news.delete_post', )
    model = Post
    template_name = 'post_delete.html'
    success_url = reverse_lazy('news')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post = self.object
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
            return HttpResponseBadRequest(f"Ошибка: {self.get_context_data()['error_message']}")
        return super().delete(request, *args, **kwargs)