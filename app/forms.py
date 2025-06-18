from django import forms
from django.contrib.auth.models import User
from app import models
from datetime import datetime

class LoginForm(forms.Form):
    username = forms.CharField(label='Username', max_length=50, widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(label='Password', widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))


    
class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Password',widget=forms.PasswordInput(attrs={'placeholder': 'Password', 'class': 'form-control'}))
    repeat_password = forms.CharField(label='Repeat Password', widget=forms.PasswordInput(attrs={'placeholder': 'Repeat Password', 'class': 'form-control'}))
    avatar = forms.ImageField(label='Avatar', required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        widgets = {'username': forms.TextInput(attrs={'placeholder': 'Username', 'class': 'form-control'}), 'email': forms.EmailInput(attrs={'placeholder': 'Email', 'class': 'form-control'})}
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        repeat_password = cleaned_data.get("repeat_password")
        if password and repeat_password and password != repeat_password:
            self.add_error('repeat_password', "Passwords do not match")
        return cleaned_data
    def save(self, commit=True):
        user = super(RegisterForm, self).save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.save()
        avatar = self.cleaned_data['avatar']
        if avatar is not None:
            models.Profile(rating=0, user=user, avatar=avatar).save()
        else:
            models.Profile(rating=0, user=user, avatar='uploads/hova.jpeg').save()
        return user
    


class AskForm(forms.ModelForm):
    title = forms.CharField(label='Title', max_length=60, widget=forms.TextInput(attrs={'placeholder': 'Title'}))
    text = forms.CharField(label='Text', widget=forms.Textarea)
    tags = forms.CharField(label='Tags', max_length=100, required=False, widget=forms.TextInput(attrs={'placeholder': '"tag1", "tag2"'}))
    class Meta:
        model = models.Quastion
        fields = ['title', 'text', 'tags']
    def clean_tags(self):
        tags = self.cleaned_data.get('tags', '')
        if not tags:
            return []
        tags_list = [tag.strip().strip('"') for tag in tags.split(',') if tag.strip()]
        if len(tags_list) > 3:
            raise forms.ValidationError('Too many tags (maximum is 3)')
        if len(tags_list) != len(set(tags_list)):
            raise forms.ValidationError('All tags must be unique')  
        return tags_list
    
    def save(self, commit=True, author=None):
        quastion = super().save(commit=False)
        quastion.author = author
        if commit:
            quastion.save()
        tags_list = self.cleaned_data.get('tags', [])
        for tag_name in tags_list:
            tag, created = models.Tag.objects.get_or_create(name=tag_name)
            quastion.tags.add(tag) 
        return quastion
    
class AnswerForm(forms.ModelForm):
    text = forms.CharField(label='Your answer', widget=forms.Textarea(attrs={'placeholder': 'I find you'}))
    class Meta:
        model = models.Answer
        fields = ['text']
    def save(self, commit=True, author=None, quastion=None):
        answer = super(AnswerForm, self).save(commit=False)
        answer.author = author
        answer.avatar = author.avatar
        answer.created_at = datetime.now()
        answer.updated_at = datetime.now()
        answer.rating = 0
        answer.quastion = quastion
        answer.save()
        quastion.answers_count+=1
        quastion.save(update_fields=['answers_count'])
        return answer
    
class SettingsForm(forms.ModelForm):
    username = forms.CharField(label='username', max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'new nickname'}))
    email = forms.CharField(label='Email', max_length=50, required=False, widget=forms.TextInput(attrs={'placeholder': 'new email'}))
    avatar = forms.ImageField(label='new avatar', required=False)
    class Meta:
        model = User
        fields = ['username', 'email', 'avatar']
    def save(self, commit=True, user=None):
        new_username = self.cleaned_data['username']
        new_email = self.cleaned_data['email']
        new_avatar = self.cleaned_data['avatar']
        profile = user.profile
        if new_username != '' and new_username != user.username:
            user.username = new_username
        if new_email != '' and new_email != user.email:
            user.email = new_email
        user.save(update_fields=['username', 'email'])
        if not (new_avatar is None) and new_avatar != profile.avatar:
            profile.avatar = new_avatar
            profile.save(update_fields=['avatar', 'user'])
        return user
