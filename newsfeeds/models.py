from django.db import models
from django.contrib.auth.models import User
from tweets.models import Tweet


class NewsFeed(models.Model):
    # 这里的 user 指能看见该 tweet 的用户，而不是创建这个 tweet 的用户
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        unique_together = (('user', 'tweet'),)
        ordering = ('-created_at',)

    def __str__(self):
        return f'{self.created_at} inbox of {self.user}: {self.tweet}'