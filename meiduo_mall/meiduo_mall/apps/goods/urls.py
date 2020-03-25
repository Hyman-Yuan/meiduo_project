from django.conf.urls import url
from . import views
urlpatterns = [
    # /list/115/1/
    url(r'^list/(?P<category_id>\d+)/(?P<page_num>\d+)/',views.ListView.as_view()),
    url(r'^hot/(?P<category_id>\d+)/',views.HotGoodsView.as_view()),
    url(r'^detail/(?P<sku_id>\d+)/',views.DetailView.as_view()),
    url(r'^visit/(?P<category_id>\d+)/',views.VisitView.as_view()),

]