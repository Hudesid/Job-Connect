from django.contrib.auth import authenticate
from rest_framework import serializers
from . import models
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.contrib.auth import get_user_model


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
        representation['profile'] = JobSeekerSerializer(instance.profile).data
        representation['date_joined'] = instance.date_joined
        representation['updated_at'] = instance.updated_at
        return representation


    def perform_update(self, serializer):
        serializer.save(is_verify_email=False, is_active=False)


