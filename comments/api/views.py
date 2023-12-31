from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from comments.models import Comment
from comments.api.serializers import (
    CommentSerializer,
    CommentSerializerForCreate,
    CommentSerializerForUpdate,
)
from comments.api.permissions import IsObjectOwner
from utils.decorators import required_params

# 不要用ModelViewSet因为会默认增删改查但我们需要给用户limited权限
class CommentViewSet(viewsets.GenericViewSet):
    """
    只实现list，create，update，destroy的方法
    不是先retrieve（查询单个 comment）的方法，因为没这个需求
    """
    serializer_class = CommentSerializerForCreate
    queryset = Comment.objects.all()
    filterset_fields = ('tweet_id',)

    # POST /api/comments/ -> create
    # GET /api/comments/ -> list
    # GET /api/comments/1/ -> retrieve
    # DELETE /api/comments/1/ -> destroy
    # PATCH /api/comments/1/ -> partial_update
    # PUT /api/comments/1/ -> update

    def get_permissions(self):
        # 注意要加用 AllowAny()/IsAuthenticated() 加括号的这种format来实例化对象
        # 而不是 AllowAny/IsAuthenticated 这样只是一个类名
        if self.action == 'create':
            return [IsAuthenticated()]
        if self.action in ['update', 'destroy']:
            # 需要先检测是否登录，再检测是否是object owner，
            # 不然anonymous client也可以是user中的一种，传进了IsObjectOwner的def里，
            # 显示的msg也会看起来不符合场景，有歧义和误导性
            return [IsAuthenticated(), IsObjectOwner()]
        return [AllowAny()]

    @required_params(params=['tweet_id'])
    def list(self,request, *args, **kwargs):
        # if 'tweet_id' not in request.query_params:
        #     return Response(
        #         {
        #             'message': 'Missing tweet_id in request',
        #             'success': False,
        #         },
        #         status=status.HTTP_400_BAD_REQUEST,
        #     )
        queryset = self.get_queryset()
        # 用prefetch_related（）先找到同样的user的id然后就取一个就可以，
        # 用created_related会left join，但当comment和user表单分开为2个独立表单时comment里不一定都会有user id
        comments = self.filter_queryset(queryset)\
            .prefetch_related('user')\
            .order_by('created_at')
        # tweet_id = request.query_params['tweet_id'] # Comment.objects.filter(tweet=tweet_id)也可以因为tweet是兼容的
        # comments = Comment.objects.filter(tweet_id=tweet_id)
        serializer = CommentSerializer(comments, many=True)
        return Response(
            {'comments': serializer.data},
            status=status.HTTP_200_OK,
        )

    def create(self, request, *args, **kwargs):
        data = {
            'user_id': request.user.id,
            'tweet_id': request.data.get('tweet_id'),
            'content': request.data.get('content'),
        }
        # 注意这里必须要加 ‘data=’ 来指定参数是传给 data 的
        # 因为默认的第一个参数是 instance
        serializer = CommentSerializerForCreate(data=data)
        if not serializer.is_valid():
            return Response({
                'message': 'Please check input',
                'errors': serializer.errors,
            }, status=status.HTTP_400_BAD_REQUEST)

        # save 方法会触发 serializer 里的 create 方法，点进 save 的具体实现里可以看到
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
        )

    def update(self, request, *args, **kwargs):
        # get_object 是 django rest framework 包装的一个函数，会在找不到的时候 raise 404 error
        # 所以这里无需做额外判断
        comment = self.get_object()
        serializer = CommentSerializerForUpdate(
            instance=comment,
            data=request.data,
        )
        if not serializer.is_valid():
            raise Response({
                'message': 'Please check input'
            }, status=status.HTTP_400_BAD_REQUEST)
        # save 方法会触发serializer 里的 update 方法，点进 save 的具体实现里可以看到
        # save 是根据 instance 参数有没有传来决定是触发 create 还是 update
        comment = serializer.save()
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_200_OK,
        )

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()
        comment.delete()
        # DRF里默认 destroy 返回的是 status code = 204 no content
        # 这里 return 了 success=True 更直观的让前端去做判断，所以 return 200 更合适
        return Response({
            'success': True
        }, status=status.HTTP_200_OK)
