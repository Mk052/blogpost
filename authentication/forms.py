from django import forms
from django.contrib.auth.forms import UserCreationForm
from authentication.models import User, Blogpost, Comment
  

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['full_name', 'email', 'password1', 'password2', 'is_email_verified']


class BlogPostForm(forms.ModelForm):
    class Meta:
        model = Blogpost
        fields = ['title', 'content', 'category']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter blog title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Write your blog content'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'row':3, 'placeholder': 'Add a comment.....'})
        }