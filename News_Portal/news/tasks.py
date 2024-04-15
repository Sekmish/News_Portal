from celery import shared_task
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.contrib.auth.models import User
from .models import Post, Subscription
from datetime import datetime, timedelta


@shared_task
def send_notification(post_id):
    post = Post.objects.get(id=post_id)
    subscribers = Subscription.objects.filter(category__in=post.categories.all()).values_list('user__email', flat=True).distinct()
    subject = f"Новая публикация: {post.title}"
    html_message = render_to_string('email/notification.html', {'post': post})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, 'pankutak@yandex.ru', list(subscribers), html_message=html_message)



@shared_task
def send_weekly_newsletter():
    last_week = datetime.now() - timedelta(days=7)
    posts = Post.objects.filter(published__gte=last_week)
    subscribers = User.objects.filter(subscriptions__isnull=False).values_list('email', flat=True).distinct()
    subject = "Еженедельная рассылка новостей"
    html_message = render_to_string('email/weekly_newsletter.html', {'posts': posts})
    plain_message = strip_tags(html_message)
    send_mail(subject, plain_message, 'pankutak@yandex.ru', list(subscribers), html_message=html_message)
