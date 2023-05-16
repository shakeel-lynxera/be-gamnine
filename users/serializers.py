import logging
import phonenumbers
from django.conf import settings
from phonenumbers.phonenumberutil import NumberParseException
from rest_framework import serializers
from twilio.base.exceptions import TwilioRestException

from utils.mock_responses import ResponseMessages
from users.models import (
    PhoneNumberOTP,
    PhoneNumberOTPTypeChoices,
    User,
    UserProfile,
)
from utils import twilio_client

logger = logging.getLogger(settings.LOGGER_NAME_PREFIX + __name__)


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(label=("phone_number"), write_only=True)
    password = serializers.CharField(
        label=("password"),
        style={"input_type": "password"},
        trim_whitespace=False,
        write_only=True,
    )
    fcm_token = serializers.CharField(label=("fcm_token"), write_only=True)

    def validate(self, attrs):

        if attrs.get("fcm_token") is None:
            raise serializers.ValidationError(ResponseMessages.FCM_TOKEN_IS_MISSING.value)

        try:
            phone_number = phonenumbers.parse(attrs.get("phone_number"))
        except NumberParseException as err:
            logger.error(err)
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        if not phonenumbers.is_valid_number(phone_number):
            logger.error(f"Invalid Phone number: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        return attrs


class RegistrationSerializer(serializers.ModelSerializer):
    token = serializers.ReadOnlyField(source="get_access_token")
    city = serializers.CharField(write_only=True)
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "fullname",
            "email",
            "phone_number",
            "password",
            "token",
            "city",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user, is_created = User.objects.update_or_create(
            fullname=validated_data["fullname"],
            email=validated_data["email"],
            phone_number=validated_data["phone_number"],
            is_active = False,
        )
        user.set_password(validated_data["password"])
        user.save()
        UserProfile.objects.update_or_create(user=user, defaults={
            "city" : validated_data.pop("city")
            })
        return user

    def validate(self, attrs):
        try:
            phone_number = phonenumbers.parse(attrs.get("phone_number"))
        except NumberParseException as err:
            logger.error(err)
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        if not phonenumbers.is_valid_number(phone_number):
            logger.error(f"Invalid Phone number: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        if User.objects.filter(phone_number=attrs["phone_number"], is_active = True).exists():
            logger.error(f"Phone number already exists: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.PHONE_NUMBER_ALREADY_EXISTS.value
            )
        if attrs["email"]:
            if User.objects.filter(email=attrs["email"], is_active = True).exists():
                logger.error(f"Email already exists: {attrs['email']}")
                raise serializers.ValidationError(
                    ResponseMessages.EMAIL_ALREADY_EXISTS.value
                )
        
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["city"] = instance.userprofile.city
        return data


class ForgetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(write_only=True)

    class Meta:
        fields = ["phone_number"]

    def validate(self, attrs):

        try:
            phone_number = phonenumbers.parse(attrs.get("phone_number"))
        except NumberParseException as err:
            logger.error(err)
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        if not phonenumbers.is_valid_number(phone_number):
            logger.error(f"Invalid Phone number: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )

        if not User.objects.filter(phone_number=attrs["phone_number"]).exists():
            logger.error(f"Invalid Phone number: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        return attrs


class VerifyOTPSerializer(serializers.ModelSerializer):
    otp = serializers.IntegerField(write_only=True)
    phone_number = serializers.CharField(write_only=True)
    otp_type = serializers.CharField(write_only=True)

    class Meta:
        model = PhoneNumberOTP
        fields = ["phone_number", "otp", "is_verified", "otp_type"]

    def validate(self, attrs):
        try:
            phone_number = phonenumbers.parse(attrs.get("phone_number"))
        except NumberParseException as err:
            logger.error(err)
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        if not phonenumbers.is_valid_number(phone_number):
            logger.error(f"Invalid Phone number: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        
        if not attrs["otp_type"] in ["signup_otp", "forgot_password_otp", "change_number_otp"]:
            raise serializers.ValidationError(
                ResponseMessages.INVALID_OTP_TYPE.value
            )

        try:
            if attrs["otp_type"] == PhoneNumberOTPTypeChoices.change_number_otp:
                instance = self.Meta.model.objects.filter(
                    phone_number = attrs["phone_number"], otp_type = attrs["otp_type"]).first()
            else:
                instance = self.Meta.model.objects.filter(
                user__phone_number=attrs["phone_number"], otp_type = attrs["otp_type"]
                ).first()
            if instance is None:
                raise serializers.ValidationError(ResponseMessages.INVALID_OTP_OR_EXPIRED.value)
            verification_check = twilio_client.verify_phone_number_with_otp(instance.twilio_service_id,
                                                                            attrs["phone_number"],
                                                                            attrs["otp"])
            if not "approved" == verification_check.status:
                logger.error("OTP invalid or expired")
                raise serializers.ValidationError(
                    ResponseMessages.INVALID_OTP_OR_EXPIRED.value
                )
        except TwilioRestException as err:
            logger.error(f" twilio exceptions: {err}")
            raise serializers.ValidationError(
                 ResponseMessages.INVALID_OTP_OR_EXPIRED.value
             )
        except Exception as err:
            logger.error(f"otp verification exceptions: {err}")
            raise serializers.ValidationError(
                 ResponseMessages.INVALID_OTP_OR_EXPIRED.value
             )
        instance.is_verified = True
        instance.save()
        return attrs


class ResetPasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["password", "confirm_password"]

    def validate(self, attrs):
        if attrs["password"] != attrs["confirm_password"]:
            logger.error("Password didn't matched.")
            raise serializers.ValidationError(ResponseMessages.PASSWORD_NOT_MATCH.value)
        return attrs

    def update(self, instance, validated_data):
        instance.set_password(validated_data["password"])
        instance.save()
        PhoneNumberOTP.objects.filter(user=instance).delete()
        return instance


class ProfileSerializer(serializers.ModelSerializer):
    city = serializers.ReadOnlyField()
    def get_city(self,object):
        return object.userprofile.city


    class Meta:
        model = User
        fields = ["fullname","city","email","phone_number"]

    def to_representation(self, objects):
        data = super().to_representation(objects)
        data["city"]=objects.userprofile.city
        return data
 

class PasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["old_password", "new_password", "confirm_password"]

    def validate(self, attrs):
        if not self.context["request"].user.check_password(attrs["old_password"]):
            logger.error("Old password didn't matched.")
            raise serializers.ValidationError(ResponseMessages.OLD_PASSWORD_NOT_MATCH.value)
        
        if attrs["new_password"] != attrs["confirm_password"]:
            logger.error("Password didn't matched.")
            raise serializers.ValidationError(ResponseMessages.PASSWORD_NOT_MATCH.value)
        
        return attrs


class PhoneNumberSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    
    class Meta:
        fields = ["phone_number"]
    
    def validate(self, attrs):
        try:
            phone_number = phonenumbers.parse(attrs.get("phone_number"))
        except NumberParseException as err:
            logger.error(err)
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        if not phonenumbers.is_valid_number(phone_number):
            logger.error(f"Invalid Phone number: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.INVALID_PHONE_NUMBER.value
            )
        if User.objects.filter(phone_number=attrs["phone_number"], is_active = True).exists():
            logger.error(f"Phone number already exists: {phone_number}")
            raise serializers.ValidationError(
                ResponseMessages.PHONE_NUMBER_ALREADY_EXISTS.value
            )
        
        return attrs
