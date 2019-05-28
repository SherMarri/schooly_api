from django.conf.urls import url

from rest_auth.views import (
    LogoutView, UserDetailsView, PasswordChangeView,
    PasswordResetView, PasswordResetConfirmView, LoginView
)

from accounts.views import CustomLoginView

urlpatterns = [
    # URLs that do not require a session or valid token
    # url(r'^password/reset/$', PasswordResetView.as_view(),
    #     name='rest_password_reset'),
    # url(r'^password/reset/confirm/$', PasswordResetConfirmView.as_view(),
    #     name='rest_password_reset_confirm'),
    url(r'^login/$', CustomLoginView.as_view(), name='rest_login'),
    # URLs that require a user to be logged in with a valid session / token.
    url(r'^logout/$', LogoutView.as_view(), name='rest_logout'),
    url(r'^me/$', UserDetailsView.as_view(), name='rest_user_details'),
    url(r'^password/change/$', PasswordChangeView.as_view(),
        name='rest_password_change'),
]