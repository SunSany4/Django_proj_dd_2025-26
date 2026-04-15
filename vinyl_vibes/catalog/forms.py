from django import forms
from .models import Album, Comment

class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        fields = ['artist', 'title', 'year', 'price', 'cover_image', 'cover_url', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'cover_url': forms.URLInput(attrs={'placeholder': 'https://...', 'class': 'form-control'}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
        labels = {
            'artist': 'Исполнитель',
            'title': 'Название альбома',
            'year': 'Год выпуска',
            'price': 'Цена (в рублях)',
            'cover_image': 'Обложка (файл)',
            'cover_url': 'Обложка (URL)',
            'description': 'Описание',
        }
        help_texts = {
            'cover_image': 'Загрузите изображение обложки (jpg, png, gif)',
            'cover_url': 'Или укажите ссылку на изображение в интернете',
        }
    
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price and price <= 0:
            raise forms.ValidationError('Цена должна быть больше нуля!')
        return price
    
    def clean_year(self):
        year = self.cleaned_data.get('year')
        if year:
            if year < 1900 or year > 2026:
                raise forms.ValidationError('Год должен быть между 1900 и 2026')
        return year
    
    def clean(self):
        cleaned_data = super().clean()
        cover_image = cleaned_data.get('cover_image')
        cover_url = cleaned_data.get('cover_url')
        print('check cover')
        # Проверяем, что хотя бы одно поле для обложки заполнено
        if not cover_image and not cover_url:
            print('no cover')
            raise forms.ValidationError('Укажите обложку альбома (загрузите файл или укажите URL)')
        
        return cleaned_data
    

    def clean(self):
        cleaned_data = super().clean()
        print(cleaned_data)
        cover_image = cleaned_data.get('cover_image')
        cover_url = cleaned_data.get('cover_url')
        if not cover_image and not cover_url:
            raise forms.ValidationError('Укажите обложку альбома (загрузите файл или укажите URL)')
        return cleaned_data



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['text']
        widgets = {
            'text': forms.Textarea(attrs={
                'rows': 3,
                'placeholder': 'Напишите ваш комментарий...',
                'class': 'form-control'
            })
        }
        labels = {
            'text': ''
        }