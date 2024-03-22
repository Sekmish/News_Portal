from django_filters import FilterSet, ModelChoiceFilter, DateFilter
from django.forms.widgets import SelectDateWidget
from .models import Post, Category
from datetime import datetime, timedelta



class CustomSelectDateWidget(SelectDateWidget):
    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        if value is None:
            label = ('День, Месяц, Год')
        return super().create_option(name, value, label, selected, index, subindex, attrs)


class NewsFilter(FilterSet):
    current_year = datetime.now().year
    years_range = range(2020, current_year + 1)

    published_after = DateFilter(
        field_name='published',
        lookup_expr='gt',
        widget=SelectDateWidget(years=years_range),
        label='Искать с ',
        method='filter_published_after'
    )

    published_before = DateFilter(
        field_name='published',
        method='filter_published_before',
        widget=SelectDateWidget(years=years_range),
        label='Искать до '
    )

    category = ModelChoiceFilter(
        field_name='categories__name',
        queryset=Category.objects.all(),
        label='Категория',
        empty_label='Все категории',
        method='filter_category',
    )

    def filter_published_before(self, queryset, name, value):
        value = value + timedelta(days=1)
        return queryset.filter(**{f'{name}__lt': value})

    def filter_published_after(self, queryset, name, value):
        queryset = queryset.filter(**{f'{name}__gt': value})
        return queryset.order_by('pk', 'published')

    class Meta:
        model = Post
        fields = {
            'title': ['icontains'],

        }

    def filter_category(self, queryset, name, value):
        if value:
            return queryset.filter(categories__name=value)
        return queryset

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['category'].field.label_from_instance = lambda obj: obj.name


