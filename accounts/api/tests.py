from testing.testcases import TestCase
from rest_framework.test import APIClient
from django.contrib.auth.models import User

LOGIN_URL = '/api/accounts/login/'
LOGOUT_URL = '/api/accounts/logout/'
SIGNUP_URL = '/api/accounts/signup/'
LOGIN_STATUS_URL = '/api/accounts/login_status/'

class AccountApiTests(TestCase):
    def setUp(self):
    # 这个函数会在每个 test function 执⾏的时候被执⾏
        self.client = APIClient()
        self.user = self.create_user(
            username='admin',
            email='admin@jiuzhang.com',
            password='correct password',
        )


    def test_login(self):
        # 每个测试函数必须以 test_ 开头，才会被⾃动调⽤进⾏测试
        # 测试必须⽤ post ⽽不是 get
        response = self.client.get(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # 登陆失败，http status code 返回 405 = METHOD_NOT_ALLOWED
        self.assertEqual(response.status_code, 405)

        # ⽤了 post 但是密码错了
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'wrong password',
        })
        self.assertEqual(response.status_code, 400)

        # 验证还没有登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

        # ⽤正确的密码
        response = self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })
        self.assertEqual(response.status_code, 200)
        self.assertNotEqual(response.data['user'], None)
        self.assertEqual(response.data['user']['email'], 'admin@jiuzhang.com')

        # 验证已经登录了
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

    #同样添加 test_logout ⽅法来测试登出：
    def test_logout(self):
        # 先登录
        self.client.post(LOGIN_URL, {
            'username': self.user.username,
            'password': 'correct password',
        })

        # 验证⽤户已经登录
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)

        # 测试必须⽤ post
        response = self.client.get(LOGOUT_URL)
        self.assertEqual(response.status_code, 405)

        # 改⽤ post 成功 logout
        response = self.client.post(LOGOUT_URL)
        self.assertEqual(response.status_code, 200)

        # 验证⽤户已经登出
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], False)

    #以及添加 test_signup ⽅法来测试注册：
    def test_signup(self):
        data = {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': 'any password',
        }
        # 测试 get 请求失败
        response = self.client.get(SIGNUP_URL, data)
        self.assertEqual(response.status_code, 405)

        # 测试错误的邮箱
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'not a correct email',
            'password': 'any password'
        })

        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 测试密码太短
        response = self.client.post(SIGNUP_URL, {
            'username': 'someone',
            'email': 'someone@jiuzhang.com',
            'password': '123',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 测试⽤户名太⻓
        response = self.client.post(SIGNUP_URL, {
            'username': 'username is tooooooooooooooooooooooooooo looooooooooooooooooooooooooooooong',
            'email': 'someone@jiuzhang.com', 'password': 'any password',
        })
        # print(response.data)
        self.assertEqual(response.status_code, 400)

        # 成功注册
        response = self.client.post(SIGNUP_URL, data)
        #self.assertEqual(response.status_code, 200)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['user']['username'], 'someone')

        # 验证⽤户已经登⼊
        response = self.client.get(LOGIN_STATUS_URL)
        self.assertEqual(response.data['has_logged_in'], True)