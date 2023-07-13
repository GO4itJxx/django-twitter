from newsfeeds.models import NewsFeed
from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase


NEWSFEEDS_URL = '/api/newsfeeds/'
POST_TWEETS_URL = '/api/tweets/'
FOLLOW_URL = '/api/friendships/{}/follow/'


class NewsFeedApiTests(TestCase):

    def setUp(self):
        self.jingxi = self.create_user('jingxi')
        self.jingxi_client = APIClient()
        self.jingxi_client.force_authenticate(self.jingxi)

        self.jiemin = self.create_user('jiemin')
        self.jiemin_client = APIClient()
        self.jiemin_client.force_authenticate(self.jiemin)

        # create followers & followings
        for i in range(2):
            follower = self.create_user('jiemin_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.jiemin)
        for i in range(3):
            following = self.create_user('jiemin_following{}'.format(i))
            Friendship.objects.create(from_user=self.jiemin, to_user=following)

    def test_list(self):
        # need login
        response = self.anonymous_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 403)
        # can not post
        response = self.jingxi_client.post(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 405)
        # nothing
        response = self.jingxi_client.get(NEWSFEEDS_URL)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['newsfeeds']), 0)
        # you can see your tweet
        self.jingxi_client.post(POST_TWEETS_URL, {'content': 'Hi there!'})
        response = self.jingxi_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 1)
        # follower can see your tweet
        self.jingxi_client.post(FOLLOW_URL.format(self.jiemin.id))
        response = self.jiemin_client.post(POST_TWEETS_URL, {
            'content': 'Howdy!',
        })
        posted_tweet_id = response.data['id']
        response = self.jingxi_client.get(NEWSFEEDS_URL)
        self.assertEqual(len(response.data['newsfeeds']), 2)
        self.assertEqual(response.data['newsfeeds'][0]['tweet']['id'], posted_tweet_id)