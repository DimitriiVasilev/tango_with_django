from django import forms
from django.contrib.auth.models import User
from .models import Page, Category, UserProfile


class CategoryForm(forms.ModelForm):
    name = forms.CharField(
        max_length=128,
        help_text='Enter a category name:'
    )
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    likes = forms.IntegerField(widget=forms.HiddenInput(), initial=0)
    # slug = forms.CharField(widget=forms.HiddenInput(), required=False)

    class Meta:
        model = Category
        fields = ('name', 'views', 'likes')


class PageForm(forms.ModelForm):
    title = forms.CharField(
        max_length=128,
        help_text='Enter the title of a page.'
    )
    url = forms.URLField(
        max_length=200,
        help_text='Enter the URL of a page.'
    )
    views = forms.IntegerField(widget=forms.HiddenInput(), initial=0)

    def clean(self):
        cleaned_data = self.cleaned_data
        url = cleaned_data.get('url')
        if url and not url.startswith('http://') and not url.startswith('https://'):
            url = 'http://' + url
            cleaned_data['url'] = url
        return cleaned_data

    class Meta:
        # Provide an association between the ModelForm and a model
        model = Page
        exclude = ('category',)


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta:
        model = User
        fields = ('username', 'email', 'password')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ('website', 'picture')
