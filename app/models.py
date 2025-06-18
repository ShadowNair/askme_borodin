from datetime import datetime, timedelta

from django.db import models
from django.contrib.auth.models import User
from django.db.models import Q, Sum, Count
from django.utils import timezone
# Create your models here.

class ProfileManager(models.Manager):
    def get_top(self):
        last_week = timezone.now() - timedelta(days=7)
        return self.annotate(total=Sum('question__rating', filter=Q(question__created_at__gte=last_week)) + 
                Sum('answer__rating', filter=Q(answer__created_at__gte=last_week))).order_by('-total')[:10]

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.PROTECT)
    avatar = models.ImageField(null=True, blank=True, upload_to="uploads", default="uploads/hova.jpeg")
    rating = models.IntegerField(default=0)
    objects = ProfileManager()
    def __str__(self):
        return str(self.user.username)

class TagManager(models.Manager):
    def get(self):
        return self.filter(quastion__created_at__gt=timezone.now() - timedelta(90)).annotate(cnt = Count("quastion")).order_by('cnt').reverse()[:10]
    
class Tag(models.Model):
    name = models.TextField(max_length=40, unique=True)
    objects = TagManager()
    def __str__(self):
        return self.name

class QuastionManager(models.Manager):
    def get_new_quastion(self):
        return self.order_by('created_at').reverse()
    def get_popular(self):
        return self.order_by('rating').reverse()
    def get_by_tag(self, tag_name):
        return self.filter(tags__name=tag_name)
    
class Quastion(models.Model):
    title = models.TextField(max_length=60)
    text = models.TextField()
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    tags = models.ManyToManyField(Tag, blank=True)
    rating = models.IntegerField(default=0)
    answers_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    objects = QuastionManager()
    def __str__(self):
        return self.title
    
class AnswerManager(models.Manager):
    def get_answers(self, quastion):
        return self.filter(quastion = quastion).order_by('correct', 'rating', '-created_at').reverse()
    
class Answer(models.Model):
    text = models.TextField()
    quastion = models.ForeignKey(Quastion, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now= True)
    rating = models.IntegerField(default=0)
    correct = models.BooleanField(default=False)
    objects = AnswerManager()
    def __str__(self):
        return self.text
    
class QuastionLike(models.Model):
    quastion = models.ForeignKey(Quastion, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    num = models.IntegerField(default=0)
    
    
        
class AnswerLike(models.Model):
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE)
    author = models.ForeignKey(Profile, on_delete=models.CASCADE)
    num = models.IntegerField(default=0)
    
    