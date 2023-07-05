from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from tweets.api.serializers import TweetSerializer, TweetSerializerForCreate
from tweets.models import Tweet



class TweetViewSet(viewsets.GenericViewSet):
    """
    API endpoint that allows users to create, list tweets
    """
    serializer_class = TweetSerializerForCreate
    #serializer_class = TweetSerializer


    def get_permissions(self):
        if self.action == 'list':
            return [AllowAny()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        """
        reload list method, not list all tweets, user_id is required as filter condition
        """
        if 'user_id' not in request.query_params:
            return Response('missing user_id', status=400)
        #this will be translated as
        #select * from twitter_tweets
        #where user_id = xxx
        #order by created_at desc
        #this sql query will use user and created_at to search
        #that means only user is not sufficient
        user_id = request.query_params['user_id']
        tweets = Tweet.objects.filter(user_id = user_id).order_by('-created_at') #desc order

        serializer = TweetSerializer(tweets, many=True)
        #in general, response in json format uses hash format as default
        #and can't use list format
        return Response({'tweets': serializer.data})

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
        return Response(TweetSerializer(tweet).data, status=201)