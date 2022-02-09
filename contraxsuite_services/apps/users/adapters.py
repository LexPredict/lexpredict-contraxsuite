"""
    Copyright (C) 2017, ContraxSuite, LLC

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as
    published by the Free Software Foundation, either version 3 of the
    License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    You can also be released from the requirements of the license by purchasing
    a commercial license from ContraxSuite, LLC. Buying such a license is
    mandatory as soon as you develop commercial activities involving ContraxSuite
    software without disclosing the source code of your own applications.  These
    activities include: offering paid services to customers as an ASP or "cloud"
    provider, processing documents on the fly in a web application,
    or shipping ContraxSuite within a closed source product.
"""
# -*- coding: utf-8 -*-

# Django imports
from typing import Optional
import regex as re
from django.contrib.auth.models import Group
from allauth.account.adapter import DefaultAccountAdapter
from allauth.account.utils import perform_login
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialLogin
from allauth.utils import build_absolute_uri
from django.conf import settings
from django.contrib.auth.forms import password_validation, PasswordResetForm, loader
from django.core.exceptions import PermissionDenied
from django.core.mail.message import EmailMultiAlternatives, EmailMessage
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from rest_auth.serializers import PasswordResetConfirmSerializer, PasswordResetSerializer, \
    UserModel, force_text, uid_decoder, default_token_generator, ValidationError
from rest_framework import serializers

from apps.common.logger import CsLogger
from apps.notifications.mail_server_config import MailServerConfig
from apps.users.models import User

__author__ = "ContraxSuite, LLC; LexPredict, LLC"
__copyright__ = "Copyright 2015-2022, ContraxSuite, LLC"
__license__ = "https://github.com/LexPredict/lexpredict-contraxsuite/blob/2.2.0/LICENSE"
__version__ = "2.2.0"
__maintainer__ = "LexPredict, LLC"
__email__ = "support@contraxsuite.com"


logger = CsLogger.get_django_logger()


class AccountAdapter(DefaultAccountAdapter):
    """
    django-allauth
    Generic account adapter.
    """
    def get_from_email(self):
        """
        This is a hook that can be overridden to programmatically
        set the 'from' email address for sending emails
        """
        from apps.common.app_vars import SUPPORT_EMAIL
        return SUPPORT_EMAIL.val() or settings.DEFAULT_FROM_EMAIL

    def render_mail(self, template_prefix, email, context):
        msg = super().render_mail(template_prefix, email, context)
        setattr(msg, 'get_connection', CustomEmailMultiAlternatives().get_connection)
        return msg

    def get_login_redirect_url(self, request):
        if request.GET and 'next' in request.GET:
            return request.GET['next']
        if request.session and 'next' in request.session:
            return request.session['next']
        return super().get_login_redirect_url(request)

    def is_open_for_signup(self, request):
        from apps.users.app_vars import ACCOUNT_ALLOW_REGISTRATION
        return ACCOUNT_ALLOW_REGISTRATION.val()

    def get_email_confirmation_url(self, request, emailconfirmation):
        url = reverse(
            "allauth_account_confirm_email",
            args=[emailconfirmation.key])
        ret = build_absolute_uri(
            None,
            url)
        return ret

    def send_mail(self, template_prefix, email, context):
        msg: EmailMessage = self.render_mail(template_prefix, email, context)
        try:
            msg.connection = MailServerConfig.make_connection_config()
        except Exception as e:
            logger.error(f'Error in getting MailServerConfig (AccountAdapter.send_mail): {e}')
            raise
        msg.send()


@receiver(post_save, sender=User)
def set_new_social_user_default_group(sender, instance: User, **kwargs):
    if not kwargs.get('created', False):
        return
    if instance.origin != User.USER_ORIGIN_SOCIAL:
        return
    from apps.users.app_vars import DEFAULT_USER_GROUP
    group_name = DEFAULT_USER_GROUP.val()
    if not group_name:
        return
    group = Group.objects.get(name=group_name)
    instance.groups.add(group)
    instance.save()


@receiver(pre_save, sender=User)
def set_new_social_user_inactive(sender, instance: User, **_kwargs):
    if instance._state.adding is not True:
        return
    if instance.id:
        return
    if instance.origin != User.USER_ORIGIN_SOCIAL:
        return

    from apps.users.app_vars import ALLOWED_EMAIL_DOMAINS, AUTO_REG_EMAIL_DOMAINS

    email = instance.email
    is_auto_reg_email = email_follows_pattern(email, AUTO_REG_EMAIL_DOMAINS.val())
    if is_auto_reg_email:
        return

    is_allowed_email = email_follows_pattern(email, ALLOWED_EMAIL_DOMAINS.val())
    if is_allowed_email:
        # this is a new social account registration - we'll make it inactive
        # until the administrator confirms the user account
        instance.is_active = False
        return
    logger.error(f'email "{email}" is not allowed')
    raise PermissionDenied()


def email_follows_pattern(email: str, pattern: Optional[str] = None) -> bool:
    from apps.users.app_vars import ALLOWED_EMAIL_DOMAINS
    if pattern is None:
        pattern = ALLOWED_EMAIL_DOMAINS.val()
    if not email or not pattern:
        return False
    at_index = email.index('@')
    if not at_index:
        return False
    email = email[at_index + 1:]

    patterns = [p for p in (pattern or '*').split(',') if p]
    if not patterns:
        return False
    for pattern in patterns:
        ptrn = '^' + pattern.replace('.', r'\.').replace('*', '.*') + '$'
        reg = re.compile(ptrn)
        for _mth in reg.finditer(email):
            return True
    return False


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """SocialAccountAdapter object"""
    def pre_social_login(self, request, sociallogin: SocialLogin):
        """
        The user is authenticated in some "social app". Consider the following
        scenarios:
        1 - the user email is found in our DB among registered users' emails
        1.1 - the user email is registered. We just "connect" the social account
              to the user "CS native" account or if these 2 accounts are already connected
              we proceed with logging in.
        1.2 - the user email is not registered. We deny the request.

        2 - the user email is not found in our DB among registered users' emails
        2.1 - the user email is registered. We register an inactive user.
        2.2 - the user email is not registered. We either allow or deny registration
              based on SOCIALACCOUNT_EMAIL_REQUIRED setting
        """

        emails = [e for e in sociallogin.email_addresses if e.primary]
        if not emails:
            return
        email_adr, email_verified = emails[0].email, emails[0].verified
        from apps.users.app_vars import SOCIALACCOUNT_EMAIL_VERIFIED_ONLY
        if SOCIALACCOUNT_EMAIL_VERIFIED_ONLY.val() and not email_verified:
            msg = f'Email "{email_adr}" is not verified'
            logger.error(msg)
            raise PermissionDenied(msg)

        try:
            user = User.objects.get(email__iexact=email_adr)
        except User.DoesNotExist:
            return

        # we're here: 1 - the user email is found in our DB among registered users' emails
        if SOCIALACCOUNT_EMAIL_VERIFIED_ONLY.val() and not email_verified:
            # 1.2 - deny the request
            msg = f'Existing email "{email_adr}" is not verified'
            logger.error(msg)
            raise PermissionDenied(msg)

        try:
            if not sociallogin.is_existing:
                sociallogin.connect(request, user)
            else:
                sociallogin.state['process'] = 'login'
                perform_login(request, user, 'none')
        except Exception as e:
            logger.error(f'Error entering social account ({email_adr}): {e}')
            raise

    def is_open_for_signup(self, request, sociallogin):
        from apps.users.app_vars import SOCIAL_ACCOUNT_ALLOW_REGISTRATION
        return SOCIAL_ACCOUNT_ALLOW_REGISTRATION.val()

    def populate_user(self,
                      request,
                      sociallogin,
                      data):
        usr = super().populate_user(request, sociallogin, data)
        usr.username = data.get('username') or data.get('email')
        return usr


class CustomPasswordChangeSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128)

    def __init__(self, *args, **kwargs):

        # TODO: made old_password field optional
        self.old_password_field_enabled = True

        self.logout_on_password_change = getattr(
            settings, 'LOGOUT_ON_PASSWORD_CHANGE', False
        )
        super().__init__(*args, **kwargs)

        if not self.old_password_field_enabled:
            self.fields.pop('old_password')

        self.request = self.context.get('request')
        self.user = getattr(self.request, 'user', None)

    def validate_old_password(self, value):
        invalid_password_conditions = (
            self.old_password_field_enabled,
            self.user,
            not self.user.check_password(value)
        )

        if all(invalid_password_conditions):
            raise serializers.ValidationError('Invalid password')
        return value

    def validate(self, attrs):
        password = attrs['new_password']
        errors = password_validation.validate_password(password, self.user)

        if errors:
            raise serializers.ValidationError(self.set_password_form.errors)
        return attrs

    def save(self):
        new_password = self.validated_data['new_password']
        self.user.set_password(new_password)
        self.user.save()
        if not self.logout_on_password_change:
            from django.contrib.auth import update_session_auth_hash
            update_session_auth_hash(self.request, self.user)


class CustomPasswordResetConfirmSerializer(PasswordResetConfirmSerializer):
    """
    Serializer for requesting a password reset e-mail.

    See custom message about wrong token
    """
    def validate(self, attrs):
        self._errors = {}

        # Decode the uidb64 to uid to get User object
        try:
            uid = force_text(uid_decoder(attrs['uid']))
            self.user = UserModel._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
            raise ValidationError({'uid': ['Invalid reset password link (wrong uid). '
                                           'Probably this link is wrong or expired. '
                                           'Please try to reset password again.']})

        self.custom_validation(attrs)
        # Construct SetPasswordForm instance
        self.set_password_form = self.set_password_form_class(
            user=self.user, data=attrs
        )
        if not self.set_password_form.is_valid():
            raise serializers.ValidationError(self.set_password_form.errors)
        if not default_token_generator.check_token(self.user, attrs['token']):
            raise ValidationError({'token': ['Invalid reset password link (wrong token). '
                                             'Probably this link is wrong or expired. '
                                             'Please try to reset password again.']})

        return attrs


class CustomEmailMultiAlternatives(EmailMultiAlternatives):

    def get_connection(self, fail_silently=False):

        from django.core.mail import get_connection
        if not self.connection:
            from apps.notifications.app_vars import get_email_backend_class
            self.connection = get_connection(

                # !!! customized backend
                backend=get_email_backend_class() or settings.EMAIL_BACKEND,
                fail_silently=fail_silently)
        return self.connection


class CustomPasswordResetForm(PasswordResetForm):

    def send_mail(self, subject_template_name, email_template_name,
                  context, from_email, to_email, html_email_template_name=None):
        """
        Send a django.core.mail.EmailMultiAlternatives to `to_email`.
        """
        subject = loader.render_to_string(subject_template_name, context)
        # Email subject *must not* contain newlines
        subject = ''.join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        from apps.common.app_vars import SUPPORT_EMAIL
        backend = MailServerConfig.make_connection_config()
        email = EmailMultiAlternatives(subject=subject,
                                       body=body,
                                       from_email=SUPPORT_EMAIL.val() or settings.DEFAULT_FROM_EMAIL,
                                       to=[to_email],
                                       connection=backend)
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email.attach_alternative(html_email, 'text/html')
        email.send(fail_silently=False)


class CustomPasswordResetSerializer(PasswordResetSerializer):
    """
    Serializer for requesting a password reset e-mail.
    """
    password_reset_form_class = CustomPasswordResetForm

    def get_email_options(self) -> dict:
        """
        Overrides default method by adding `extra_email_context`.
        """
        from apps.common.app_vars import SUPPORT_EMAIL
        return {
            'subject_template_name': 'registration/password_reset_subject.txt',
            'html_email_template_name': 'registration/password_reset_email.html',
            'extra_email_context': {
                'support_email': SUPPORT_EMAIL.val(),
            }
        }

    def save(self):
        """
        Overrides default method by adding AppVar to `from_email`.
        """
        request = self.context.get('request')
        from apps.common.app_vars import SUPPORT_EMAIL
        opts = {
            'use_https': request.is_secure(),
            'from_email': SUPPORT_EMAIL.val() or getattr(settings, 'DEFAULT_FROM_EMAIL'),
            'request': request,
        }
        opts.update(self.get_email_options())
        self.reset_form.save(**opts)
