from django.db import models

# Create your models here.
from django.contrib.auth.models import User
#from datetime import datetime
from utils.time_helpers import utc_now

class Tweet(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null = True,
        help_text= 'who posts this tweet',
        #verbose_name='HiTweeter'
    )
    content = models.CharField(max_length = 255)
    created_at = models.DateTimeField(auto_now_add=True)
    #updated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user','created_at'),) #tuple 2元组，之后index会有很多所以会套括号
        ordering = ('user', '-created_at') #排序规则不套括号了因为规则就一个

    @property
    def hours_to_now(self):
        #return (datetime.now() - self.created_at).seconds // 3600
        return (utc_now() - self.created_at).seconds // 3600

    @property
    def comments(self):
        return self.comment_set.all()
        # return Comment.objects.filter(tweet=self)
    def __str__(self):
        #这里是在执行print（tweet instance）的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'