from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.contrib.admin import SimpleListFilter
from .models import Author, Category, Post, PostCategory, Comment, Subscription


class CategoryFilter(SimpleListFilter):
    title = _('Категории')
    parameter_name = 'categories'

    def lookups(self, request, model_admin):
        categories = Category.objects.all()
        return [(category.id, category.name) for category in categories]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(categories__id=self.value())
        return queryset


class PostAdmin(admin.ModelAdmin):
    list_display = ('get_title', 'get_categories', 'get_post_type', 'get_published')
    list_filter = (CategoryFilter,)

    def get_title(self, obj):
        return obj.title

    get_title.short_description = _('Заголовок')

    def get_categories(self, obj):
        return ', '.join(category.name for category in obj.categories.all())

    get_categories.short_description = _('Категории')

    def get_post_type(self, obj):
        return obj.get_post_type_display()

    get_post_type.short_description = _('Тип публикации')

    def get_published(self, obj):
        return obj.published

    get_published.short_description = _('Дата публикации')


admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Post, PostAdmin)
admin.site.register(PostCategory)
admin.site.register(Comment)
admin.site.register(Subscription)
