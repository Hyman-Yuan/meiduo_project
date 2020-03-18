from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^areas/$',views.GetAreaView.as_view()),
]