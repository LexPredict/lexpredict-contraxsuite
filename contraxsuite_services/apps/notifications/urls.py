from django.conf.urls import url

from .views import SendDigestTaskView, RenderDigestView, DigestImageView, NotificationImageView, RenderNotificationView

# URL pattern list
urlpatterns = []

urlpatterns += [

    url(
        r'^send-digest/$',
        SendDigestTaskView.as_view(),
        name='send-digest',
    ),
    url(
        r'^digest_configs/(?P<config_id>\d+)/render.(?P<content_format>\w+)$',
        RenderDigestView.as_view(),
        name='render-digest',
    ),
    url(
        r'^digest_configs/(?P<config_id>\d+)/images/(?P<image_fn>.+)$',
        DigestImageView.as_view(),
        name='digest-image',
    ),
    url(
        r'^notification_subscriptions/(?P<subscription_id>\d+)/render.(?P<content_format>\w+)$',
        RenderNotificationView.as_view(),
        name='render-notification',
    ),
    url(
        r'^notification_subscriptions/(?P<subscription_id>\d+)/images/(?P<image_fn>.+)$',
        NotificationImageView.as_view(),
        name='notification-image',
    ),
]
