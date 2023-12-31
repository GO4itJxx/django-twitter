from rest_framework.test import APIClient
from testing.testcases import TestCase
from tweets.models import Tweet


# 注意要加 ‘/’ 结尾，要不然会产生 301 redirect
# 注意开头也别忘加 ‘/’，要不然会产生 404 not found
TWEET_LIST_API = '/api/tweets/'
TWEET_CREATE_API = '/api/tweets/'
TWEET_RETRIEVE_API = '/api/tweets/{}/'

class TweetApiTests(TestCase):

    def setUp(self):

        self.user1 = self.create_user('user1', 'user1@qq.com')
        self.tweets1 = [
            self.create_tweet(self.user1)
            for i in range(3)
        ]

        self.user1_client = APIClient()
        self.user1_client.force_authenticate(self.user1)

        self.user2 = self.create_user('user2','user2@qq.com')
        self.tweets2 = [
            self.create_tweet(self.user2)
            for i in range(2)
        ]

    def test_list_api(self):
        # 必须带 user_id
        response = self.anonymous_client.get(TWEET_LIST_API)
        self.assertEqual(response.status_code, 400)

        #正常 request
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user1.id})
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(response.data['tweets']), 3)
        response = self.anonymous_client.get(TWEET_LIST_API, {'user_id': self.user2.id})
        self.assertEqual(len(response.data['tweets']), 2)
        # 检测排序是按照新创建的在前面的顺序来的, 第0位的是后发的帖子，第1位的是前一个发的帖子
        # 前者是unicode string后者是UUID，是不同的object所以要转换成一种，UUID转string
        self.assertEqual(response.data['tweets'][0]['id'], str(self.tweets2[1].id))
        self.assertEqual(response.data['tweets'][1]['id'], str(self.tweets2[0].id))

    def test_create_api(self):
        # 必须登录
        response = self.anonymous_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 403)


        # 必须带content
        response = self.user1_client.post(TWEET_CREATE_API)
        self.assertEqual(response.status_code, 400)


        # content不能太短
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '1'})
        self.assertEqual(response.status_code, 400)


        # content不能太长
        response = self.user1_client.post(TWEET_CREATE_API, {'content': '0' * 141})
        self.assertEqual(response.status_code, 400)


        # 正常发贴
        tweets_count = Tweet.objects.count()
        response = self.user1_client.post(TWEET_CREATE_API, {
            'content': 'Hey there! THIS IS MY 1ST TWEET :)'
        })
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['id'], self.user1.id)
        self.assertEqual(Tweet.objects.count(), tweets_count + 1)

    def test_retrieve_api(self):
        url = TWEET_RETRIEVE_API.format(-1)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 404)

        tweet = self.create_tweet(self.user1)
        url = TWEET_RETRIEVE_API.format(tweet.id)
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['comments']), 0)

        self.create_comment(self.user2, tweet, 'holly molly!!!')
        self.create_comment(self.user1, tweet, 'hmm...')
        self.create_comment(self.user1, self.create_tweet(self.user2), '...')
        response = self.anonymous_client.get(url)
        self.assertEqual(len(response.data['comments']), 2)