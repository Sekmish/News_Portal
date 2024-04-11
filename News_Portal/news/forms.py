from django import forms
from django.core.exceptions import ValidationError

from .models import Post

class PostSearchForm(forms.ModelForm):
    content = forms.CharField(min_length=20)
    class Meta:
        model = Post
        fields = [
            'title',
            'content',

        ]





class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['author', 'title', 'content', 'rating', 'categories']
        widgets = {
            'rating': forms.HiddenInput(attrs={'value': 0}),
            'author': forms.Select(),

        }

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        self.fields['rating'].required = False
        self.fields['author'].empty_label = 'Выберите автора'


    def clean(self): #используется если надо проверить несколько полей
        cleaned_data = super().clean()

        content = cleaned_data.get('content')
        if content is not None and len(content) < 20:
            raise ValidationError({'content': 'Описание не может быть менее 20 символов.'})

        name = cleaned_data.get('title')
        if name == content:
            raise ValidationError('Описание не должно быть идентично названию.')

        return cleaned_data


    def clean_name(self): # Если требуется проверить одно поле сложным образом, создайте для этого метод clean_fieldname.
        title = self.cleaned_data['title']
        if title[0].islower():
            raise ValidationError('Название должно начинаться с заглавной буквы.')
        return title