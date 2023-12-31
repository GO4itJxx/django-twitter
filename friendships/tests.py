from django.test import TestCase
# from friendships.models import Friendship
# from friendships.services import FriendshipService
# from testing.testcases import TestCase
#
#
# class FriendshipServiceTests(TestCase):
#
#     def setUp(self):
#         self.clear_cache()
#         self.jingxi = self.create_user('jingxi')
#         self.jiemin = self.create_user('jiemin')
#
#     def test_get_followings(self):
#         user1 = self.create_user('user1')
#         user2 = self.create_user('user2')
#         for to_user in [user1, user2, self.jiemin]:
#             Friendship.objects.create(from_user=self.jingxi, to_user=to_user)
#         FriendshipService.invalidate_following_cache(self.jingxi.id)
#
#         user_id_set = FriendshipService.get_following_user_id_set(self.jingxi.id)
#         self.assertSetEqual(user_id_set, {user1.id, user2.id, self.jiemin.id})
#
#         Friendship.objects.filter(from_user=self.jingxi, to_user=self.jiemin).delete()
#         FriendshipService.invalidate_following_cache(self.jingxi.id)
#         user_id_set = FriendshipService.get_following_user_id_set(self.jingxi.id)
#         self.assertSetEqual(user_id_set, {user1.id, user2.id})