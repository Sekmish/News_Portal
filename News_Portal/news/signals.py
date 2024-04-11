from django.db.models.signals import m2m_changed
from django.dispatch import receiver
from django.core.mail import EmailMultiAlternatives
from django.template.defaultfilters import truncatewords_html
from django.conf import settings
from .models import Category, Subscription, Post


@receiver(m2m_changed, sender=Post.categories.through)
def notify_subscribers(sender, instance, action, pk_set, **kwargs):
    if action == 'post_add':
        # Получаем категории, к которым был добавлен пост
        categories = Category.objects.filter(pk__in=pk_set)

        for category in categories:
            # Находим всех подписчиков категории
            subscriptions = Subscription.objects.filter(category=category)
            for subscription in subscriptions:
                # Отправляем письмо каждому подписчику
                send_subscription_email(subscription.user, instance)


def send_subscription_email(user, post):
    # Формируем сообщение
    subject = f'Новый пост в категории {post.categories.first().name}'
    truncated_content = truncatewords_html(post.content, 10,)
    # Подготавливаем содержимое письма
    text_content = (
        f'Здравствуйте, {user.username}!\n\n'
        f'Вы подписаны на категорию {post.categories.first().name}, и там появилась новая публикация:\n'
        f'Название: {post.title}\n'
        f'Краткое описание: {truncated_content}\n\n'
        f'Читать полностью: {settings.SITE_DOMAIN}{post.get_absolute_url()}'
    )

    html_content = (
        f'<h4>Здравствуйте, {user.username}!</h4>'
        f'<p>Вы подписаны на категорию {post.categories.first().name}, и там появилась новая публикация:</p>'
        f'<p>Название: {post.title}</p>'
        f'<p>Краткое описание: {truncated_content}</p>'
        f'<p><a href="{settings.SITE_DOMAIN}{post.get_absolute_url()}">Читать полностью</a></p>'
    )

    # Отправляем письмо
    msg = EmailMultiAlternatives(
        subject,
        text_content,
        settings.EMAIL_HOST_USER,
        [user.email]
    )

    msg.attach_alternative(html_content, "text/html")
    msg.send()