from comments.models import Comment
from django.utils import timezone
from rest_framework.test import APIClient
from testing.testcases import TestCase

COMMENT_URL = '/api/comments/'
COMMENT_DETAIL_URL = '/api/comments/{}/'

class CommentApiTests(TestCase):

    def setUp(self):
        # 创建user并创建对应client再把client登录好
        self.jingxi = self.create_user('jingxi')
        self.jingxi_client = APIClient()
        self.jingxi_client.force_authenticate(self.jingxi)
        self.jiemin = self.create_user('jiemin')
        self.jiemin_client = APIClient()
        self.jiemin_client.force_authenticate(self.jiemin)
        # 创建1个帖子
        self.tweet = self.create_tweet(self.jingxi)

    def test_create(self):
        # 匿名不可以创建
        response = self.anonymous_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 403)

        # 什么参数都没带不可以
        response = self.jingxi_client.post(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # 只带 tweet_id 不行
        response = self.jingxi_client.post(COMMENT_URL, {'tweet_id': self.tweet.id})
        self.assertEqual(response.status_code, 400)


        # 只带 content 不行
        response = self.jingxi_client.post(COMMENT_URL, {'content':'1'})
        self.assertEqual(response.status_code, 400)


        # content太长不行
        response = self.jingxi_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1' * 141,
        })
        self.assertEqual(response.status_code, 400)
        self.assertEqual('content' in response.data['errors'], True)

        # tweet_id 和 content 都有才可以
        response = self.jingxi_client.post(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'content': '1',
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.jingxi.id)
        self.assertEqual(response.data['tweet_id'], self.tweet.id)
        self.assertEqual(response.data['content'], '1')

    def test_destroy(self):
        comment = self.create_comment(self.jingxi, self.tweet)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # 匿名不可以删除
        response = self.anonymous_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # 非本人不能删除
        response = self.jiemin_client.delete(url)
        self.assertEqual(response.status_code, 403)

        # 本人可以删除
        count = Comment.objects.count()
        response = self.jingxi_client.delete(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Comment.objects.count(), count - 1)

    def test_update(self):
        comment = self.create_comment(self.jingxi, self.tweet, 'original')
        another_tweet = self.create_tweet(self.jiemin)
        url = COMMENT_DETAIL_URL.format(comment.id)

        # 使用 put 的情况下
        # 匿名不可以更新
        response = self.anonymous_client.delete(url, {'content':'new'})
        self.assertEqual(response.status_code, 403)
        # 非本人不能更新
        response = self.jiemin_client.delete(url, {'content':'new'})
        self.assertEqual(response.status_code, 403)
        comment.refresh_from_db()
        self.assertNotEqual(comment.content, 'new')
        # 不能更新除 content 外的内容，静默处理，只更新内容
        before_update_at = comment.updated_at
        before_create_at = comment.created_at
        now = timezone.now()
        response = self.jingxi_client.put(url, {
            'content': 'new',
            'user_id': self.jiemin.id,
            'tweet_id': another_tweet.id,
            'create_at': now
        })
        self.assertEqual(response.status_code, 200)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'new')
        self.assertEqual(comment.user, self.jingxi)
        self.assertEqual(comment.tweet, self.tweet)
        self.assertEqual(comment.created_at, before_create_at)
        self.assertNotEqual(comment.created_at, now)
        self.assertNotEqual(comment.updated_at, before_update_at)

    def test_list(self):
        # 必须带 tweet_id
        response = self.anonymous_client.get(COMMENT_URL)
        self.assertEqual(response.status_code, 400)

        # 带了 tweet.id 可以访问
        # 一开始没有评论
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        # 评论按照时间顺序
        self.create_comment(self.jingxi, self.tweet, '1')
        self.create_comment(self.jiemin, self.tweet, '2')
        self.create_comment(self.jiemin, self.create_tweet(self.jiemin), '3')
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
        })
        self.assertEqual(len(response.data['comments']), 2)
        self.assertEqual(response.data['comments'][0]['content'], '1')
        self.assertEqual(response.data['comments'][1]['content'], '2')

        # 同时提供 user_id 和 tweet_id 只有 tweet_id 会在 filter 中生效
        response = self.anonymous_client.get(COMMENT_URL, {
            'tweet_id': self.tweet.id,
            'user_id': self.jingxi.id,
        })
        self.assertEqual(len(response.data['comments']), 2)