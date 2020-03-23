from django.conf.urls import url
from . import views
urlpatterns = [
    # /list/115/1/
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/$',views.ListView.as_view()),

]