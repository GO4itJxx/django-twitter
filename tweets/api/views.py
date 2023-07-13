from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import (
    TweetSerializer,
    TweetSerializerForCreate,
    TweetSerializerWithComments,)
from tweets.models import Tweet
from utils.decorators import required_params
from newsfeeds.services import NewsFeedService

class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows users to create, list tweets
    """
    serializer_class = TweetSerializerForCreate
    #serializer_class = TweetSerializer
    queryset = Tweet.objects.all()

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    #@required_params(request_attr='query_params', params=['user_id'])
    @required_params(params=['user_id'])
    def list(self, request, *args, **kwargs):
        """
        reload list method, not list all tweets, user_id is required as filter condition
        """
        # if 'user_id' not in request.query_params:
        #     return Response('missing user_id', status=400)
        #this will be translated as
        #select * from twitter_tweets
        #where user_id = xxx
        #order by created_at desc
        #this sql query will use user and created_at to search
        #that means only user is not sufficient
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id=user_id).order_by('-created_at') #desc order
        serializer = TweetSerializer(tweets, many=True)
        #in general, response in json format uses hash format as default
        #and can't use list format
        return Response({'tweets': serializer.data})

    def retrieve(self, request, *args, **kwargs):
        tweet = self.get_object() #throw 404
        return Response(TweetSerializerWithComments(tweet).data)
    def create(self, request, *args, **kwargs):
        """
        reload create method, need use current login user as tweets.user
        """
        serializer = TweetSerializerForCreate(
            data=request.data,
            context={'request':request},
        )
        if not serializer.is_valid():
            return Response({
                'success': False,
                'message': "Please check input",
                'errors': serializer.errors,
            }, status=400)
        #save will call create method in TweetSerializerForCreate
        tweet = serializer.save()
        NewsFeedService.fanout_to_followers(tweet)
        return Response(TweetSerializer(tweet).data, status=201)