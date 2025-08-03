from rest_framework import serializers
from .models import Project, Environment, API, TestCase, TestStep, TestExecution
from rest_framework import serializers
# from .models import User


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class EnvironmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Environment
        fields = '__all__'
        read_only_fields = ('created_at',)

#
class APISerializer(serializers.ModelSerializer):
    class Meta:
        model = API
        fields = '__all__'
        read_only_fields = ('created_at',)


class TestStepSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestStep
        fields = '__all__'
        read_only_fields = ('created_at',)


class TestCaseSerializer(serializers.ModelSerializer):
    steps = TestStepSerializer(many=True, read_only=True)
    class Meta:
        model = TestCase
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')


class TestExecutionSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestExecution
        fields = '__all__'
        read_only_fields = ('start_time', 'duration', 'report', 'created_at')


# class UserProfileSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserProfile
#         fields = ['avatar', 'bio']


# class UserSerializer(serializers.ModelSerializer):
#     profile = UserProfileSerializer(required=False)
#
#     class Meta:
#         model = User
#         fields = ['id', 'username', 'email', 'first_name', 'last_name',
#                   'role', 'phone', 'department', 'is_active', 'profile']
#         extra_kwargs = {
#             'password': {'write_only': True},
#             'is_active': {'read_only': True}
#         }
#
#     def create(self, validated_data):
#         profile_data = validated_data.pop('profile', None)
#         password = validated_data.pop('password', None)
#         user = User(**validated_data)
#         if password:
#             user.set_password(password)
#         user.save()
#
#         if profile_data:
#             UserProfile.objects.create(user=user, **profile_data)
#
#         return user
#
#     def update(self, instance, validated_data):
#         profile_data = validated_data.pop('profile', None)
#         password = validated_data.pop('password', None)
#
#         for attr, value in validated_data.items():
#             setattr(instance, attr, value)
#
#         if password:
#             instance.set_password(password)
#
#         instance.save()
#
#         if profile_data:
#             profile = instance.profile
#             for attr, value in profile_data.items():
#                 setattr(profile, attr, value)
#             profile.save()
#
#         return instance
#

# class RolePermissionSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = RolePermission
#         fields = '__all__'