from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.db.models import Exists, OuterRef
from .models import Subscription, Category
import logging

logger = logging.getLogger(__name__)

@login_required
@csrf_protect
def subscription_view(request):
    categories_with_posts = Category.objects.filter(
        post__isnull=False
    ).distinct().annotate(
        is_subscribed=Exists(
            Subscription.objects.filter(user=request.user, category=OuterRef('pk'))
        )
    ).order_by('name')

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
