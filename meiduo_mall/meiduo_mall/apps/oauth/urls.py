from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^qq/authorization/$',views.QQAuthView.as_view()),
    url(r'oauth_callback$',views.QQUserAuthView.as_view()),
]