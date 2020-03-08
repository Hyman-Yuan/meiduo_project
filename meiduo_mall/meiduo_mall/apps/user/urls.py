from django.conf.urls import url
from . import views


# 请求路由 http://127.0.0.1:8000/register
urlpatterns = [
    url(r'^register/$',views.RegisterView.as_view()),
]