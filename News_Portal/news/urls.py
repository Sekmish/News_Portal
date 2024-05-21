from django.urls import path
from .viewses import list_views, detail_view, create_view, update_view, delete_view
from .views import subscription_view
from django.views.decorators.cache import cache_page

urlpatterns = [
    path('', list_views.PostList.as_view(), name='news'),
    path('<int:pk>', detail_view.PostDetail.as_view(), name='post_detail'),
    path('search/', list_views.PostSearchList.as_view()),
    path('<str:post_type>/create/', create_view.PostCreate.as_view(), name='post_create'),
    path('<str:post_type>/<int:pk>/update/', update_view.PostUpdate.as_view(), name='post_update'),
    path('<str:post_type>/<int:pk>/delete/', delete_view.PostDelete.as_view(), name='post_delete'),
    path('subscriptions/', subscription_view, name='subscription_view'),
]
