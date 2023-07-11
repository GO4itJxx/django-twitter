from accounts.api.serializers import UserSerializerForComment
from comments.models import Comment
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet

class CommentSerializer(serializers.ModelSerializer):
    user = UserSerializerForComment()

    class Meta:
        model = Comment
        fields = (
            'id',
            'tweet_id',
            'user',
            'content',
            'created_at',
            'updated_at',
        )

class CommentSerializerForCreate(serializers.ModelSerializer):
    # 这两项必须手动添加
    # 因为默认 ModelSerializer 里只会自动包含 user 和 tweet 而不是 user_id 和 tweet_id
    tweet_id = serializers.IntegerField()
    user_id = serializers.IntegerField()

    class Meta:
        model = Comment
        fields = (
            'content',
            'tweet_id',
            'user_id'
        )

    def validate(self, data):
        tweet_id = data['tweet_id']
        if not Tweet.objects.filter(id=tweet_id).exists():
            raise ValidationError({'message': 'tweet does not exist'})
        # 必须 return validated data
        # 也就是验证过之后，进行处理的（当然也可以不做处理）输入数据
        return data

    def create(self, validated_data):
        return Comment.objects.create(
            user_id=validated_data['user_id'],
            tweet_id=validated_data['tweet_id'],
            content=validated_data['content'],
        )

#不可以在CommentSerializerForCreate里创建update和destroy
# 1.可以改的fields不同，tweet_id 和 user_id是不可更改的
# 即便之后有些项目里可以改但不建议，因为分开之后做更新和修改会方便很多
class CommentSerializerForUpdate(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('content',)
    def update(self, instance, validated_data):
         instance.content = validated_data['content']
         instance.save()
         # update 方法要求 return 修改后的 instance 作为返回值
         return instance