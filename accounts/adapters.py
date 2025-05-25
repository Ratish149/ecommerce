from allauth.headless.adapter import DefaultHeadlessAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from rest_framework_simplejwt.tokens import RefreshToken
from typing import Dict, Any
from allauth.account.utils import user_display, user_username, user_field, user_email
from allauth.account.models import EmailAddress
from allauth.utils import valid_email_or_none
from django.contrib.auth.models import Group
from datetime import datetime
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def populate_user(self, request, sociallogin, data):
        """
        Hook that can be used to further populate the user instance.

        For convenience, we populate several common fields.

        Note that the user instance being populated represents a
        suggested User instance that represents the social user that is
        in the process of being logged in.

        The User instance need not be completely valid and conflict
        free. For example, verifying whether or not the username
        already exists, is not a responsibility.
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

        user = user.save()
        return user


class CustomHeadlessAdapter(DefaultHeadlessAdapter):
    """
    Custom headless adapter that extends DefaultHeadlessAdapter to include token functionality.
    """

    def serialize_user(self, user) -> Dict[str, Any]:
        """
        Returns the basic user data. Note that this data is also exposed in
        partly authenticated scenario's (e.g. password reset, email
        verification).
        """
        ret = {
            "display": user_display(user),
            "has_usable_password": user.has_usable_password(),
        }
        if user.pk:
            ret["id"] = user.pk
            email = EmailAddress.objects.get_primary_email(user)
            if email:
                ret["email"] = email
        username = user_username(user)
        try:
            refresh = RefreshToken.for_user(user)
            refresh['user_type'] = user.user_type
            refresh['email'] = user.email
            refresh['first_name'] = user.first_name
            refresh['last_name'] = user.last_name
            refresh['phone'] = user.phone
            refresh['address'] = user.address
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
        Saves a new User instance using information provided in the
        signup form.
        """
        import json

        # Parse the JSON data from request.body
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            # If request.body is already parsed (e.g. by middleware), use it directly
            data = request.body
        print('User adapter')
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")
        phone = data.get("phone", "")
        address = data.get("address", "")
        email = data.get("email")
        # Use email as username if not provided
        username = data.get("username", email)
        user_email(user, email)
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
            # Ability not to commit makes it easier to derive from
            # this adapter by adding
            user.save()
        return user

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        current_site = get_current_site(request)
        activate_url = self.get_email_confirmation_url(
            request, emailconfirmation)
        ctx = {
            "user": emailconfirmation.email_address.user,
            "activate_url": activate_url,
            "current_site": current_site,
            "key": emailconfirmation.key,
        }
        subject = render_to_string(
            'account/email/email_confirmation_message_subject.txt', ctx).strip()
        text_body = render_to_string(
            'account/email/email_confirmation_message_message.txt', ctx)
        html_body = render_to_string(
            'account/email/email_confirmation_message.html', ctx)
        msg = EmailMultiAlternatives(subject, text_body, None, [
                                     emailconfirmation.email_address.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send()
