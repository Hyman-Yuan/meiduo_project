from django.conf.urls import url
from . import views


# 配置文件修改后,域名改为:www.meiduo.site
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
    # http://127.0.0.1:8000/logout
    url(r'^info/$', views.InfoView.as_view()),
    url(r'^emails/$', views.EmailView.as_view()),
    url(r'^emails/verification/$', views.EmailVerifyView.as_view()),
    # url(r'^addresses/$',views.AddressView.as_view()),
    # url(r'^addresses/create/$',views.AddressCreateView.as_view()),
    url(r'^addresses/$',views.AddressDisplayView.as_view()),
    url(r'^addresses/create/$',views.CreateAddressView.as_view()),
    # 修改地址/删除地址
    url(r'^addresses/(?P<address_id>[\d]+)/$',views.UpdateAddressView.as_view()),
    # 修改地址标题
    url(r'^addresses/(?P<address_id>[\d]+)/title/$',views.UpdateAddressTitleView.as_view()),
    # 设置默认地址
    url(r'^addresses/(?P<address_id>[\d]+)/default/$',views.SetDefaultAddressView.as_view()),
    # user browse history
    url(r'^browse_histories/$', views.BrowseHistoryView.as_view()),
]