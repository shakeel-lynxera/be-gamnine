from enum import Enum


class ResponseMessages(str, Enum):
    # User registration messages
    SOMETHING_MISSING_IN_REQUEST = "Something is missing in request body."
    ACCOUNT_CREATED = "Account created successfully."
    INVALID_PHONE_NUMBER = "Invalid phone number."
    IN_VALID_PHONE_NUMBER_OR_PASSWORD = "Invalid phone number or password."
    LOGGED_IN_SUCCESSFULLY = "Logged in successfully."
    SOMETHING_MISSING_IN_FORGET_PASSWORD_REQUEST = (
        "Something is missing in forget password request body."
    )
    PHONE_NUMBER_OTP_SENT = "Phone number OTP sent successfully."
    EMAIL_OTP_SENT = "OTP has been sent succesfuly sent."
    INVALID_OTP_OR_EXPIRED = "Invalid OTP or expired."
    SOMETHING_MISSING_IN_VERIFY_PASSWORD_REQUEST = (
        "Something is missing in verify password request body."
    )
    OTP_VERIFIED = "OTP verified successfully."
    PASSWORD_NOT_MATCH = "Password not match."
    PHONE_NUMBER_MISSING = "Phone number is missing."
    PHONE_NUMBER_NOT_EXIST = "Phone number does not exist."
    SOMETHING_MISSING_IN_RESET_PASSWORD_REQUEST = (
        "Something is missing in reset password request body."
    )
    PASSWORD_RESET = "Password reset successfully."
    OLD_PASSWORD_NOT_MATCH = "Old password not match."
    EMAIL_CHANGED = "Email changed successfully."
    INVALID_OTP_TYPE = "Invalid OTP type."
    PHONE_NUMBER_ALREADY_EXISTS = "Phone number already exists."
    OTP_NOT_VERIFIED = "OTP not verified."
    PHONE_NUMBER_CHANGED = "Phone number changed successfully."
    EMAIL_ALREADY_EXISTS = "Email already exists."
    TICKET_CREATED = "Ticket created successfully."
    NOT_FOUND = "Not found."
    SUCCESS = "Success."
    INVALID_CATEGORY = "Invalid category."
    INVALID_PROPERTY_ID = "Invalid property id."
    FCM_TOKEN_IS_MISSING = "FCM token is missing."
