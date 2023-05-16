from email.policy import default
import logging
from django.core.mail import send_mail
from django.contrib.auth import authenticate
from rest_framework import status
from utils.reuseable import generate_six_length_random_number
from gemnineDealerBackend.settings import (EMAIL_HOST_USER, EMAIL_HOST_PASSWORD,EMAIL_HOST,EMAIL_PORT)
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        )

from baselayer.baseapiviews import BaseAPIView
from baselayer.baseauthentication import JWTAuthentication
from utils.mock_responses import ResponseMessages
from gemnineDealerBackend import settings
from users.models import (
    PhoneNumberOTP,
    PhoneNumberOTPTypeChoices,
    TempUserEmail,
    User,
)
from users.serializers import (
    ForgetPasswordSerializer,
    LoginSerializer,
    RegistrationSerializer,
    ResetPasswordSerializer,
    VerifyOTPSerializer,
    ProfileSerializer,
    PasswordSerializer,
    PhoneNumberSerializer,
)
from utils.baseutils import (
    get_first_error_message_from_serializer_errors,
)
from utils.twilio_client import send_phone_number_verification_sms

logger = logging.getLogger(settings.LOGGER_NAME_PREFIX + __name__)


class RegistrationView(BaseAPIView):
    """User registration APIView"""

    permission_classes = [AllowAny]
    serializer_class = RegistrationSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        """Register a new user.

        Example:
            Request Body:
                API URL: http://baseurl/users/registration/
                {
                    "fullname": "Shakeel Afridi",
                    "phone_number": "+92316151****",
                    "email": "shakeel@domin.com",
                    "password": "pass@word",
                    "city": "Islamabad",
                }

            Response Body:
                {
                    "success": true,
                    "payload": {},
                    "message": "OTP sent successfully."
                }

        """
        serializer_registration = self.serializer_class(data=request.data)
        if not serializer_registration.is_valid():
            logger.error(serializer_registration.errors)
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=serializer_registration.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_REQUEST,
                )
            )
        user = serializer_registration.save()
        try:
            phone_number = request.data.get("phone_number")
            service_id = send_phone_number_verification_sms(phone_number)
            user = User.objects.get(phone_number = phone_number)
            PhoneNumberOTP.objects.update_or_create(user = user, otp_type=PhoneNumberOTPTypeChoices.signup_otp,
                                                    defaults = {'twilio_service_id': service_id.sid})
        except Exception as e:
            print(e)
        return self.send_success_response(
            message=ResponseMessages.PHONE_NUMBER_OTP_SENT
        )


class SignInView(BaseAPIView):
    """User Sign in APIView
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    queryset = User.objects.all()

    def post(self, request, *args, **kwargs):
        # User.objects.filter(phone_number="+923420202688").delete()
        """Login end user

        Example:
            Request Body:
                API URL: http://users/sign-in/
                {
                    "phone_number": "+92316151***",
                    "password": "pass@word"
                }
            Response Body:
                {
                    "success": true,
                    "payload": {
                        "token": "jwt-token"
                    },
                    "message": "Logged in successfully."
                }
        """

        serializer_login = self.serializer_class(data=request.data)
        if not serializer_login.is_valid():
            logger.error(serializer_login.errors)
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=serializer_login.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_REQUEST,
                )
            )

        user = authenticate(
            phone_number=request.data.get("phone_number"),
            password=request.data.get("password"),
        )
        if not user:
            return self.send_response(
                success=False,
                message=ResponseMessages.IN_VALID_PHONE_NUMBER_OR_PASSWORD,
                status_code=status.HTTP_401_UNAUTHORIZED,
            )

        token = user.get_access_token()
        user.fcm_token = request.data.get("fcm_token")
        user.save()
        return self.send_success_response(
            message=ResponseMessages.LOGGED_IN_SUCCESSFULLY, payload={"token": token,
                                                                      "fullname": user.fullname,
                                                                      "email": user.email,
                                                                      "phone_number": user.phone_number,
                                                                      "city":user.userprofile.city})
        

class ForgetPasswordAPIView(BaseAPIView):
    """Forget Password APIView for user"""

    permission_classes = [AllowAny]
    serializer_class = ForgetPasswordSerializer

    def post(self, request, *args, **kwargs):
        """Forget Password
        Example:
            Request Body:
                API URL: http://baseurl/users/forget-password/
                Body:
                    {
                        "phone_number": ""
                    }
            Response Body:
                {
                    "success": true,
                    "message": "Phone number OTP sent successfully.."
                }
        """
        forget_password_serializer = self.serializer_class(data=request.data)
        if not forget_password_serializer.is_valid():
            logger.error(forget_password_serializer.errors)
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=forget_password_serializer.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_FORGET_PASSWORD_REQUEST,
                )
            )
        try:
            phone_number = request.data.get("phone_number")
            service_id = send_phone_number_verification_sms(phone_number)
            user = User.objects.filter(phone_number = phone_number).first()
            PhoneNumberOTP.objects.update_or_create(user=user,
                                                             otp_type=PhoneNumberOTPTypeChoices.forgot_password_otp,
                                                    defaults = {'twilio_service_id': service_id.sid})
        except Exception as e:
            print(e)
        return self.send_success_response(
            message=ResponseMessages.PHONE_NUMBER_OTP_SENT
        )


class VerifyOTPAPIView(BaseAPIView):
    """Verify OTP APIView for user"""
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def patch(self, request, *args, **kwargs):
        """Verify OTP
        Example:
        Request Body:
        API URL: http://baseurl/users/verify-otp/
        Request Body:
            {
                "phone_number":"+9231190+++++",
                "otp" : "opt value",
                "otp_type": "string"
            }
        Response Body:
            {
                "success": true,
                "payload": {""},
                "message": "OTP verified successfully."
            }
        """
        payload = {}
        verify_otp_serializer = self.serializer_class(data=request.data)
        if not verify_otp_serializer.is_valid():
            logger.error(verify_otp_serializer.errors)
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=verify_otp_serializer.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_VERIFY_PASSWORD_REQUEST,
                )
            )
        if verify_otp_serializer.validated_data.get("otp_type") == PhoneNumberOTPTypeChoices.signup_otp:
            user = User.objects.filter(phone_number = verify_otp_serializer.validated_data.get("phone_number")).first()
            user.is_active = True
            user.save()
            payload = {
                "fullname": user.fullname,
                "email": user.email,
                "number": user.phone_number,
                "city":user.userprofile.city
            }
            message = ResponseMessages.ACCOUNT_CREATED
            PhoneNumberOTP.objects.filter(
                user__phone_number=verify_otp_serializer.validated_data.get("phone_number")
            ).delete()
        
        elif verify_otp_serializer.validated_data.get("otp_type") == PhoneNumberOTPTypeChoices.forgot_password_otp:
            user = User.objects.filter(phone_number = verify_otp_serializer.validated_data.get("phone_number")).first()
            message = ResponseMessages.OTP_VERIFIED
            PhoneNumberOTP.objects.filter(
                user=user, otp_type=PhoneNumberOTPTypeChoices.forgot_password_otp
            ).update(is_verified = True)
        
        elif verify_otp_serializer.validated_data.get("otp_type") == PhoneNumberOTPTypeChoices.change_number_otp:
            phone_number = verify_otp_serializer.validated_data.get("phone_number")
            instance = PhoneNumberOTP.objects.filter(phone_number=phone_number).first()
            instance.user.phone_number = phone_number
            instance.user.save()
            user = User.objects.filter(phone_number = phone_number).first()
            user.phone_number = verify_otp_serializer.validated_data.get("phone_number")
            user.save()
            user = User.objects.filter(phone_number = phone_number).first()
            message = ResponseMessages.PHONE_NUMBER_CHANGED,
            instance.delete()

        token = user.get_access_token()
        payload.update({"token": token})
        return self.send_success_response( message=message, payload=payload)


class ResetPasswordAPIView(BaseAPIView):
    """User resetting password"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = ResetPasswordSerializer
    queryset = User.objects.all()

    def patch(self, request, *args, **kwargs):
        """User Reset Password
        Example:
            API URL: http://baseurl/users/reset-password/
            Header: Authorization: Bearer <token>
            Request Body:
                {
                    "password":"1234",
                    "confirm_password":"1234"
                }
            Response Body:
                {
                    "success": true,
                    "payload": {},
                    "message": "Password reset successfully."
                }
        """
        if not PhoneNumberOTP.objects.filter(user=request.user,
                                             otp_type = PhoneNumberOTPTypeChoices.forgot_password_otp,
                                             is_verified = True
                                             ).exists():
            return self.send_bad_request_response(
                message=ResponseMessages.OTP_NOT_VERIFIED
            )
        reset_password_serializer = self.serializer_class(request.user, data=request.data)
        if not reset_password_serializer.is_valid():
            logger.error(reset_password_serializer.errors)
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=reset_password_serializer.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST,
                )
            )
        reset_password_serializer.save()
        return self.send_success_response(message=ResponseMessages.PASSWORD_RESET)


class ProfileView(BaseAPIView):
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    def get(self, request):
        """User Get Profile
        Example:
            API URL: http://baseurl/users/profile/
            Authorization: Bearer <token>
            Method: GET
            Response Body:
                {
                 "fullname": "usman",
                 "city": "Islamabad",
                 "email": "usman@emai.com",
                 "phone_number": "+92311907++++",   
                }
        """
        profile_data= self.serializer_class(request.user)
        return self.send_success_response(message="success",payload=profile_data.data)

    def patch(self,request):
        """User Update Profile
        Example:
            API URL: http://baseurl/users/profile/
            Authorization: Bearer <token>
            Method: PATCH
            Request Body:
                {
                    "fullname": "usman",
                    "city": "islamabad"
                }
            Response Body:
                {
                 "fullname": "usman",
                 "city": "Islamabad",
                 "email": "usman@emai.com",
                 "phone_number": "+92311907++++",   
                }
        """
        update_data = self.serializer_class(request.user,request.data,partial = True)
        if not update_data.is_valid():
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=update_data.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST,
                )
            )
        update_data.save()
        request.user.userprofile.city=request.data["city"]
        request.user.userprofile.save()
        return self.send_success_response(message="update",payload=self.serializer_class(request.user).data)
    

class EmailView(BaseAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    
    def patch(self,request):
        if not request.data.get("email"):
            return self.send_bad_request_response(message="email is missing")
        email= request.data.get("email")
        if User.objects.filter(email=email).exists():
            return self.send_bad_request_response(message="email already exists")
        otp = generate_six_length_random_number()
        try:
            send_mail("GEMNINE TECH OTP: ", otp, EMAIL_HOST_USER, [email])
        except Exception as e:
            print(e)
        TempUserEmail.objects.update_or_create(user=request.user, defaults={"otp":otp,
                                                                            "email":email})
        return self.send_success_response(message=ResponseMessages.EMAIL_OTP_SENT)


class VerifyEmailOTPView(BaseAPIView):
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    
    def patch(self, request):
        if not request.data.get("email"):
            return self.send_bad_request_response(message="Email is missing")
        if not request.data.get("otp"):
            return self.send_bad_request_response(message="OTP is missing")

        if not TempUserEmail.objects.filter(email=request.data.get("email"),
                                            otp=request.data.get("otp"),
                                            user=request.user).exists():
            return self.send_bad_request_response(message="invalid otp.")
        
        request.user.email = request.data.get("email")
        request.user.save()
        token = request.user.get_access_token()
        return self.send_success_response(message=ResponseMessages.EMAIL_CHANGED,
                                          payload={"token": token})


class PasswordAPIView(BaseAPIView):
    """User resetting password"""

    permission_classes = [IsAuthenticated]
    serializer_class = PasswordSerializer
    authentication_classes = [JWTAuthentication]

    def patch(self, request, *args, **kwargs):
        """User Reset Password
        Example:
            API URL: http://baseurl/users/reset-password/
            Request Body:
                {
                    "old_password": "old_password",
                    "password": "new_password",
                    "confirm_password": "new_password"
                }
            Response Body:
                {
                    "success": true,
                    "payload": {},
                    "message": "Password reset successfully."
                }
        """
        reset_password_serializer = self.serializer_class(data=request.data, context = {"request": request})
        if not reset_password_serializer.is_valid():
            logger.error(reset_password_serializer.errors)
            return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=reset_password_serializer.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST,
                )
            )
        request.user.set_password(reset_password_serializer.validated_data["new_password"])
        request.user.save()
        return self.send_success_response(message=ResponseMessages.PASSWORD_RESET)


class PhoneNumberView(BaseAPIView):
    """User changing phone number"""
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]
    serializer_class = PhoneNumberSerializer

    def patch(self,request):
        try:
            serializer_data = self.serializer_class(data=request.data)
            if not serializer_data.is_valid():
                return self.send_bad_request_response(
                message=get_first_error_message_from_serializer_errors(
                    serialized_errors=serializer_data.errors,
                    default_message=ResponseMessages.SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST,
                )
            )
            phone_number = serializer_data.validated_data["phone_number"]
            service_id = send_phone_number_verification_sms(phone_number)
            PhoneNumberOTP.objects.update_or_create(user=request.user, otp_type = PhoneNumberOTPTypeChoices.change_number_otp,
                                                    defaults={
                                                        "twilio_service_id": service_id.sid,
                                                        "phone_number": phone_number
                                                        }
                                                    )
        except Exception as e:
            print(e)
        return self.send_success_response(
            message=ResponseMessages.PHONE_NUMBER_OTP_SENT
        )
