from django.conf.urls import url


urlpatterns = [
    url(r'^register/$',
        'registration_api.views.register',
        name='registration_api_register'),
    url(r'^activate/(?P<activation_key>\w+)/$',
        'registration_api.views.activate',
        name='registration_activate'),
]
