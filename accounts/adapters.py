from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Dict, Any
from allauth.account.utils import user_display, user_username, user_field, user_email
from allauth.account.models import EmailAddress
from allauth.utils import valid_email_or_none
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import json


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Populate the user instance with additional fields from the social provider.
        """
        first_name = data.get("first_name")
        last_name = data.get("last_name")
        email = data.get("email")
        name = data.get("name")
        username = data.get("username")
        phone = data.get("phone")
        address = data.get("address")

        user = sociallogin.user
        user_username(user, username or "")
        user_email(user, valid_email_or_none(email) or "")
        name_parts = (name or "").partition(" ")
        user_field(user, "first_name", first_name or name_parts[0])
        user_field(user, "last_name", last_name or name_parts[2])

        if phone:
            user_field(user, "phone", phone)
        if address:
            user_field(user, "address", address)

        user.save()
        return user


class CustomHeadlessAdapter(DefaultHeadlessAdapter):
    """
    Custom headless adapter with token functionality.
    """

    def serialize_user(self, user) -> Dict[str, Any]:
        """
        Serialize user and return basic info along with JWT tokens.
        """
        ret = {
            "display": user_display(user),
            "has_usable_password": user.has_usable_password(),
        }

        if user.pk:
            ret["id"] = user.pk
            # Safe retrieval of email address
            email_obj = EmailAddress.objects.filter(
                user=user, primary=True).first()
            if email_obj:
                ret["email"] = email_obj.email

        username = user_username(user)

        try:
            refresh = RefreshToken.for_user(user)
            # Safely add custom claims
            refresh["email"] = getattr(user, "email", "")
            refresh["first_name"] = getattr(user, "first_name", "")
            refresh["last_name"] = getattr(user, "last_name", "")
            refresh["phone"] = getattr(user, "phone", "")
            refresh["address"] = getattr(user, "address", "")
            ret["access_token"] = str(refresh.access_token)
            ret["refresh_token"] = str(refresh)
        except Exception as e:
            print(f"Error creating token: {e}")

        if username:
            ret["username"] = username
        return ret


class CustomAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new User instance using information provided in the signup form or request.
        """
        try:
            if hasattr(request, "data"):
                data = request.data
            else:
                data = json.loads(request.body.decode())
        except Exception as e:
            print(f"Failed to parse request body: {e}")
            data = {}

        print('User adapter')

        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        phone = data.get("phone", "")
        address = data.get("address", "")
        email = data.get("email")
        username = data.get("username", email)

        user_email(user, email)
        user.email = email
        user_username(user, username)

        if first_name:
            user_field(user, "first_name", first_name)
        if last_name:
            user_field(user, "last_name", last_name)
        if phone:
            user_field(user, "phone", phone)
        if address:
            user_field(user, "address", address)

        if "password1" in data:
            user.set_password(data["password1"])
        elif "password" in data:
            user.set_password(data["password"])
        else:
            user.set_unusable_password()

        self.populate_username(request, user)

        if commit:
            user.save()

        return user

    def is_open_for_signup(self, request):
        """
        Allow signup to proceed.
        """
        return True

    def should_send_confirmation_mail(self, request, email_address, signup) -> bool:
        """
        Override to prevent sending confirmation emails since we auto-verify.
        """
        return False  # Don't send confirmation emails

    def is_email_verified(self, request, email):
        """
        Always return True to indicate email is verified by default.
        """
        return True

    def confirm_email(self, request, email_address):
        """
        Override to auto-verify emails when they are created.
        """
        from allauth.account.internal.flows import email_verification

        # Mark as verified before calling the parent method
        email_address.verified = True
        email_address.save()

        # Call the parent method to handle other verification logic
        return email_verification.verify_email(request, email_address)

    def stash_verified_email(self, request, email):
        """
        Override to mark email as verified in session.
        """
        request.session["account_verified_email"] = email
        super().stash_verified_email(request, email)
