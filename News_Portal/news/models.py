from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum, F

class RatingMixin(models.Model):
    rating = models.IntegerField(default=0)

    def like(self):
        try:
            self.rating += 1
            self.save()
        except Exception as e:
            print(f"Ошибка при увеличении рейтинга: {e}")

    def dislike(self):
        try:
            self.rating -= 1
            self.save()
        except Exception as e:
            print(f"Ошибка при уменьшении рейтинга: {e}")

    class Meta:
        abstract = True

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rating = models.IntegerField()

    def update_rating(self):
        try:
            posts_rating = self.post_set.aggregate(posts_rating=Sum('rating'))['posts_rating'] or 0
            comments_rating = Comment.objects.filter(post__author=self).aggregate(comments_rating=Sum('rating'))['comments_rating'] or 0
            self.rating = posts_rating * 3 + comments_rating
            self.save(update_fields=['rating'])
        except Exception as e:
            print(f"Ошибка при обновлении рейтинга автора: {e}")

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

class Post(RatingMixin):
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    post_type = models.CharField(max_length=20, choices=[('article', 'Article'), ('news', 'News')])
    created_at = models.DateTimeField(auto_now_add=True)
    categories = models.ManyToManyField(Category, through='PostCategory')
    title = models.CharField(max_length=200)
    content = models.TextField()
    rating = models.IntegerField()


    def preview(self):
        try:
            return (self.content[:124] + '...') if len(self.content) > 124 else self.content
        except Exception as e:
            print(f"Ошибка при генерации предпросмотра: {e}")
            return self.content


    def update_rating(self):
        try:
            self.rating = self.comment_set.aggregate(Sum('rating'))['rating__sum'] or 0
            self.save(update_fields=['rating'])
        except Exception as e:
            print(f"Ошибка при обновлении рейтинга статьи: {e}")

class PostCategory(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)

class Comment(RatingMixin):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    rating = models.IntegerField()
