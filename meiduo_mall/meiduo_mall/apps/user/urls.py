from django.conf.urls import url
from . import views



urlpatterns = [
    # 请求路由 http://127.0.0.1:8000/register
    url(r'^register/$',views.RegisterView.as_view()),
    # usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/
    url(r'^usernames/(?P<username>[a-zA-Z0-9_-]{5,20})/count/$',views.UsernameCountView.as_view()),
    # mobiles//(?P<mobile>1[3-9]\d{9})/count/
    url(r'^mobiles/(?P<mobile>1[3-9]\d{9})/count/$',views.MobileCountView.as_view()),
]