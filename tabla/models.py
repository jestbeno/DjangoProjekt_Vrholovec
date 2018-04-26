from django.db import models
from django.contrib.auth.models import User
from django.utils.text import Truncator
from django.utils.html import mark_safe
from markdown import markdown
import math

class Tabla(models.Model):
    name = models.CharField(max_length=30,unique=True)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def get_posts_count(self):
        return Post.objects.filter(ideja__tabla=self).count()

    def get_last_post(self):
        return Post.objects.filter(ideja__tabla=self).order_by('-created_at').first()

class Ideja(models.Model):
    subject = models.CharField(max_length=100)
    last_updated = models.DateTimeField(auto_now_add=True)
    tabla = models.ForeignKey(Tabla, related_name='ideje',on_delete=models.CASCADE)
    starter = models.ForeignKey(User,related_name='ideje',on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)
    def __str__(self):
        return self.subject

    def get_page_count(self):
        count = self.posts.count()
        pages = count / 10
        return math.ceil(pages)

    def has_many_pages(self, count=None):
        if count is None:
            count = self.get_page_count()
        return count > 6

    def get_page_range(self):
        count = self.get_page_count()
        if self.has_many_pages(count):
            return range(1, 5)
        return range(1, count + 1)
    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]



class Post(models.Model):
    message = models.TextField(max_length=4000)
    ideja = models.ForeignKey(Ideja,related_name='posts',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User,related_name='posts',on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User,null=True,related_name='+',on_delete=models.CASCADE)

    def __str__(self):
        # In the Post model we are using the Truncator utility class. It’s a convenient way to truncate long strings into an arbitrary string size (here we are using 30).
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))

# TESTNO FILANJE BAZE
# python manage.py shell
#
# from django.contrib.auth.models import User
# from boards.models import Board, Topic, Post
#
# user = User.objects.first()
#
# board = Board.objects.get(name='Django')
#
# for i in range(100):
#     subject = 'Topic test #{}'.format(i)
#     topic = Topic.objects.create(subject=subject, board=board, starter=user)
#     Post.objects.create(message='Lorem ipsum...', topic=topic, created_by=user)
#

