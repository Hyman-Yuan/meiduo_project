from django.conf.urls import url
from . import views
urlpatterns = [
    # url(r'^/$',views..as_view()),
    url(r'^orders/settlement/$',views.OrderSettlementView.as_view()),
    url(r'^/orders/commit/$', views.OrderCommitView.as_view()),
]