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

    @property
    def hours_to_now(self):
        #return (datetime.now() - self.created_at).seconds // 3600
        return (utc_now() - self.created_at).seconds // 3600

    def __str__(self):
        #这里是在执行print（tweet instance）的时候会显示的内容
        return f'{self.created_at} {self.user}: {self.content}'