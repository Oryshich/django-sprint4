from django import forms
from django.contrib.auth import get_user_model

from .models import Comment, Post


User = get_user_model()


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        widgets = {
            'pub_date': forms.DateInput(
                attrs={'type': 'date'},
                format='%Y-%m-%d'
            )
        }
        exclude = ('author',)


class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('text',)


class EditUserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
