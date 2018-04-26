from django import forms
from .models import Ideja, Post

class NewIdejaForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'Vnesi sporočilo..'}
        ),
        max_length=4000,
        help_text='Maksimalna dolžina niza je 4000 znakov.',
        label='Sporočilo'
    )

    class Meta:
        model = Ideja
        fields = ['subject', 'message']
        labels = {
            'subject': 'Nova ideja',
        }

class PostForm(forms.ModelForm):
    message = forms.CharField(
        widget=forms.Textarea(
            attrs={'rows': 5, 'placeholder': 'Vnesi sporočilo..'}
        ),
        max_length=4000,
        help_text='Maksimalna dolžina niza je 4000 znakov.',
        label='Sporočilo'
    )
    class Meta:
        model = Post
        fields = ['message', ]