from django import forms
from .models import Note

class NoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': '输入你的思路、错因、解法记录等'
            }),
        }
        labels = {
            'content': '笔记内容',
        }
