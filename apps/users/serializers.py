from django.contrib.auth import authenticate
from django.db import transaction
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken

from . import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError


class CustomTokenObtainSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        username_or_email = attrs.get(self.username_field)
        password = attrs.get('password')
        User = get_user_model()

        try:
            user = User.objects.get(username=username_or_email)
        except User.DoesNotExist:
            try:
                user = User.objects.get(email=username_or_email)
            except User.DoesNotExist:
                raise serializers.ValidationError('No user found with the provided credentials')

        if not user.check_password(password):
            raise serializers.ValidationError('No active account found with the given credentials')

        if not user.is_active:
            raise serializers.ValidationError('User account is not active')

        authenticate_kwargs = {
            self.username_field: username_or_email,
            'password': password
        }

        request = self.context.get('request')
        if request:
            authenticate_kwargs['request'] = request
        else:
            raise serializers.ValidationError('Request context missing')

        user = authenticate(**authenticate_kwargs)

        if user is None:
            raise serializers.ValidationError('No active account found with the given credentials')

        data = super().validate(attrs)
        return data


class UserDataForGetRequestsSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.JobSeeker
        fields = ('id', 'username', 'email', 'user_type', 'date_joined', 'updated_at')


class JobSeekerSerializer(serializers.ModelSerializer):
    profile_photo = serializers.ImageField(required=False, allow_null=True)
    resume = serializers.FileField(required=False, allow_null=True)
    phone_number = serializers.CharField(min_length=12)

    class Meta:
        model = models.JobSeeker
        fields = ('id', 'first_name', 'last_name', 'date_of_birth', 'phone_number', 'location', 'bio', 'skills', 'experience_years', 'education_level', 'profile_photo', 'resume')


    def create(self, validated_data):
        skills_data = validated_data.pop("skills", [])
        if models.JobSeeker.objects.filter(user=self.context['request'].user).exists():
            raise serializers.ValidationError("You have a profile, you can't create a second profile.")
        job_seeker = models.JobSeeker.objects.create(user=self.context['request'].user, **validated_data)
        job_seeker.skills.set(skills_data)
        job_seeker.save()
        return job_seeker

    def update(self, instance, validated_data):
        user_data = validated_data.pop("user", [])

        if user_data:
            for key, value in user_data.items():
                setattr(instance.user, key, value)
            instance.user.is_active = False
            instance.user.is_verify_email = False
            instance.user.save()

        for x, y in validated_data.items():
            setattr(instance, x, y)

        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        from apps.skills.serializers import SkillSerializer
        representation['skills'] = SkillSerializer(instance.skills, many=True).data
        representation['user'] = UserSerializer(instance.user).data
        return representation

class CompanySerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=False, allow_null=True)

    class Meta:
        model = models.Company
        fields = ('id', 'created_at', 'updated_at', 'name', 'description', 'website', 'industry', 'location', 'founded_year', 'employees_count', 'logo')


    def perform_create(self, serializer):
        serializer.save(user=self.context['request'].user)

    def perform_update(self, serializer):
        serializer.save(user=self.context['request'].user)


    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['user'] = UserDataForGetRequestsSerializer(instance.user).data
        representation['is_active'] = instance.is_active
        return representation


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = models.User
        fields = ('id', 'username', 'email', 'password', 'user_type')



    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['date_joined'] = instance.date_joined
        representation['updated_at'] = instance.updated_at
        return representation


    def perform_update(self, serializer):
        serializer.save(is_verify_email=False, is_active=False)



class VerifyEmailSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    token = serializers.CharField()

    def validate(self, attrs):
        pk = attrs['pk']
        token = attrs['token']

        try:
            user = models.User.objects.get(id=pk)
            token = models.Token.objects.get(token=token)

        except models.User.DoesNotExist:
            raise serializers.ValidationError({"error": "The user ID is wrong"})

        except models.Token.DoesNotExist:
            raise serializers.ValidationError({"error": "The token is wrong"})

        if token.expires_at <= timezone.now() and not user.is_verify_email:
            with transaction.atomic():
                token.delete()
                user.delete()
            raise serializers.ValidationError(
                {"error": f"Token vaqti o'tib ketdi shu sababli {user.username} o'chirib tashlandi."}
            )

        user.is_active = True
        user.is_verify_email = True
        user.save()
        token.delete()
        attrs['user'] = UserSerializer(user).data
        return attrs


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, attrs):
        email = attrs['email']
        if not email:
            raise serializers.ValidationError({"error": "Email kiritish muhum."})

        try:
            user = models.User.objects.get(email=email)

        except models.User.DoesNotExist:
            raise serializers.ValidationError({"error": "Foydalanuvchi bunday email bilan topilmadi."})

        attrs['user'] = user
        return attrs


class RecoveryPasswordGetSerializer(serializers.Serializer):
    pk = serializers.IntegerField()
    token = serializers.CharField()


    def validate(self, attrs):
        pk = attrs['pk']
        token = attrs['token']

        try:
            user = models.User.objects.get(id=pk)
            token = models.Token.objects.get(token=token)

        except models.User.DoesNotExist:
            raise serializers.ValidationError({"error": "Foydalanuvchi bunday ID bilan topilmadi."})

        except models.Token.DoesNotExist:
            raise serializers.ValidationError({"error": "Token serverda topilmadi."})

        if token is None:
            raise serializers.ValidationError({'error': "Token bo'lishi shart."})

        if token.expires_at <= timezone.now():
            raise serializers.ValidationError(
                {"error": f"Token vaqti o'tib ketdi shu sababli token o'chirib tashaldi."}
            )

        attrs['user'] = UserSerializer(user).data
        return attrs


class RecoveryPasswordPostSerializer(serializers.Serializer):
    new_password = serializers.CharField(write_only=True, min_length=8)


    def validate(self, attrs):
        new_password = attrs['new_password']
        id = self.context['pk']
        token = self.context['token']
        user = models.User.objects.get(id=id)
        token = models.Token.objects.get(token=token)

        if not new_password:
            raise serializers.ValidationError({"error": "Parol kiritish shart."})

        if not user:
            raise serializers.ValidationError({"error": "Foydalanuvchi bu id bilan hali topilmadi."})

        if not token:
            raise serializers.ValidationError({"error": "Foydalanuvchi bu token bilan topilmadi"})

        user.set_password(new_password)
        user.save()
        token.delete()
        attrs['user'] = UserSerializer(user).data
        return attrs


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField()


    def validate(self, attrs):
        refresh = attrs['refresh_token']
        try:
            if not refresh:
                raise serializers.ValidationError({"error": "Refresh token is required."})

            token = RefreshToken(refresh)
            token.blacklist()


        except TokenError as e:
            raise serializers.ValidationError({"errors": f"Token error: {str(e)}"})

        except Exception as e:
            raise serializers.ValidationError({"errors": f"An error occurred: {str(e)}"})

        attrs['user'] = UserSerializer(self.context['request'].user).data
        return attrs
