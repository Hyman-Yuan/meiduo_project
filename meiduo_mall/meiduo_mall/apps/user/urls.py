from django.conf.urls import url
from . import views



urlpatterns = [
    # http://127.0.0.1:8000/register
    url(r'^register/$',views.RegisterView.as_view()),
    # http://127.0.0.1:8000/usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',views.UsernameCountView.as_view()),
    # http://127.0.0.1:8000/mobiles//(?P<mobile>1[3-9]\d{9})/count/
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.MobileCountView.as_view()),
    # http://127.0.0.1:8000/login
    url(r'^login/$',views.LoginView.as_view()),
    # http://127.0.0.1:8000/logout
    url(r'^logout/$', views.LogoutView.as_view()),
]