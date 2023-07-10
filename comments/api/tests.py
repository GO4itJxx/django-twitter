from testing.testcases import TestCase
from rest_framework.test import APIClient

COMMENT_URL = '/api/comments/'

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
            'content': '1' * 141
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
