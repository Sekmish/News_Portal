from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.cache import cache


class RatingMixin(models.Model):
    """
    Миксин для моделей с рейтингом
    """
    rating = models.IntegerField(default=0)

    def like(self):
        """
        Увеличение рейтинга на 1
        """
        self.rating += 1
        self.save()

    def dislike(self):
        """
        Уменьшение рейтинга на 1
        """
        self.rating -= 1
        self.save()

    class Meta:
        abstract = True


class Author(models.Model):
    """
    Автор статей
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def update_rating(self):
        """
        Обновление рейтинга автора
        """
        posts_rating = self.post_set.aggregate(posts_rating=Sum('rating')).get('posts_rating') or 0
        comments_rating = Comment.objects.filter(post__author=self).aggregate(comments_rating=Sum('rating')).get('comments_rating') or 0
        self.rating = posts_rating * 3 + comments_rating
        self.save(update_fields=['rating'])

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Автор"
        verbose_name_plural = 'Авторы'


class Category(models.Model):
    """
    Категория статей
    """
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = 'Категории'


class Post(RatingMixin):
    """
    Статья
    """
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=20, choices=[('article', 'Статья'), ('news', 'Новость')])
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    content = models.TextField()
    published = models.DateTimeField(auto_now=True, db_index=True)

    def preview(self):
        """
        Возвращает предпросмотр статьи
        """
        return self.content[:124] + '...' if len(self.content) > 124 else self.content

    def update_rating(self):
        """
        Обновление рейтинга статьи
        """
        self.rating = self.comment_set.aggregate(Sum('rating')).get('rating__sum') or 0
        self.save(update_fields=['rating'])

    def __str__(self):
        return f'{self.title.title()}: {self.content[:20]}'

    def get_absolute_url(self):
        return reverse('post_detail', args=[str(self.id)])

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        cache.delete(f'post-{self.pk}')

    class Meta:
        verbose_name = "Публикация"
        verbose_name_plural = 'Публикации'


@receiver(post_save, sender=Post)
def send_notification_on_post_create(sender, instance, created, **kwargs):
    """
    Отправка уведомления при создании новой статьи
    """
    if created:
        from .tasks import send_notification  # Импорт здесь, чтобы избежать циклической зависимости
        send_notification.delay(instance.id)


class PostCategory(models.Model):
    """
    Связь между статьей и категорией
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.post.title} - {self.category.name}'

    class Meta:
        verbose_name = "Категория публикации"
        verbose_name_plural = 'Категории публикаций'


class Comment(RatingMixin):
    """
    Комментарий к статье
    """
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий"
        verbose_name_plural = 'Комментарии'


class Subscription(models.Model):
    """
    Подписка на категорию
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subscribers')
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.username} подписан на {self.category.name}'

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'category')  # Гарантирует, что пользователь может подписаться на категорию только один раз.

