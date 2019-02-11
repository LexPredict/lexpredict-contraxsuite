from django.conf.urls import url

from apps.imanage_integration import views

# URL pattern list
urlpatterns = []

urlpatterns += [

    url(
        r'^imanage-sync/$',
        views.IManageSyncTaskView.as_view(),
        name='imanage-sync',
    ),
]
