from django.conf.urls import patterns, url


urlpatterns = patterns(
    '',
    url(r'^register/$',
        'registration_api.views.register',
        name='registration_api_register'),
)
