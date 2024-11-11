from django.contrib.auth.models import User  # User 모델
# Django의 기본 패스워드 검증 도구
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate
# Django의 기본 authenticate 함수, 우리가 설정한 DefaultAuthBackend인 TokenAuth 방식으로 유저를 인증해줌

from rest_framework import serializers
from rest_framework.authtoken.models import Token  # Token 모델
from rest_framework.validators import UniqueValidator  # 이메일 중복 방지를 위한 검증 도구

from .models import Profile


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        help_text="이메일(Unique)",
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())],
    )
    password = serializers.CharField(
        help_text="비밀번호",
        write_only=True,
        required=True,
        validators=[validate_password],
    )
    password2 = serializers.CharField(
        help_text="비밀번호 재입력", write_only=True, required=True,)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email')

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."})

        return data

    def create(self, validated_data):
        # CREATE 요청에 대해 create 메소드를 오버라이딩, 유저를 생성하고 토큰을 생성하게함
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
        )

        user.set_password(validated_data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return user

# 클라이언트가 보내줬을떄 확인하여 해당하는 토큰을 응답하기만 하면 되기 때문에 ModelSerializer를 사용할 필요가 없다.
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=True)
    password = serializers.CharField(required=True, write_only=True)
    # write_only : 클라이언트 서버 방향의 역직렬화는 가능 서버 클라이언트 방향의 직렬화는 불가능

    def validate(self, data):
        user = authenticate(**data)
        if user:
            token = Token.objects.get(user=user)
            return token
        # user라면 토큰을 보내기만 한다
        raise serializers.ValidationError(
            {"error": "Unable to log in with provided credentials."})

# ModelSerializer를 사용, 추가한 Profile의 Model들
class ProfileSerializer(serializers.ModelSerializer):
    
    # class Meta:
    #     model = User
    #     fields = ('username', 'password', 'password2', 'email')
    class Meta:
        model = Profile
        fields = ("nickname", "position", "subjects", "image")