from django.urls import path
from .views import PostList, PostDetail, PostSearch, PostCreate, PostUpdate, PostDelete, subscription_view
from django.views.decorators.cache import cache_page


urlpatterns = [
    path('', cache_page(60)(PostList.as_view()), name='news'),
    path('<int:pk>', PostDetail.as_view(), name='post_detail'),
    path('search/', PostSearch.as_view()),
    path('<str:post_type>/create/', PostCreate.as_view(), name='post_create'),
    path('<str:post_type>/<int:pk>/update/', PostUpdate.as_view(), name='post_update'),
    path('<str:post_type>/<int:pk>/delete/', PostDelete.as_view(), name='post_delete'),
    path('subscriptions/', subscription_view, name='subscription_view'),
]
