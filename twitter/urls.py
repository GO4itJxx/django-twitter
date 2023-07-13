"""twitter URL Configuration

The `urlpatterns` list routes URLs to views.py. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views.py
    1. Add an import:  from my_app import views.py
    2. Add a URL to urlpatterns:  path('', views.py.home, name='home')
Class-based views.py
    1. Add an import:  from other_app.views.py import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

#import debug_toolbar
from accounts.api.views import UserViewSet, AccountViewSet
from comments.api.views import CommentViewSet
from django.contrib import admin
from django.urls import include, path
from rest_framework import routers
from tweets.api.views import TweetViewSet
from friendships.api.views import FriendshipViewSet

router = routers.DefaultRouter()
#for only from accounts.api import views
#router.register(r'api/users', views.py.UserViewSet)
#router.register(r'api/accounts', views.AccountViewSet, basename='accounts')
router.register(r'api/users', UserViewSet)
router.register(r'api/accounts', AccountViewSet, basename='accounts')
router.register(r'api/tweets', TweetViewSet, basename='tweets')
router.register(r'api/comments', CommentViewSet, basename='comments')
router.register(r'api/friendships', FriendshipViewSet, basename = 'friendships')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    #path('__debug__/', include(debug_toolbar.urls)),
]
