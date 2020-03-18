from django.shortcuts import render
from django.views import View
from django import http
from .models import Area
from meiduo_mall.utils.response_code import RETCODE
from django.core.cache import cache


# Create your views here.
class GetAreaView(View):
    def get(self,request):
        # 查询省市区 areas/?area_id=
        area_id = request.GET.get('area_id')
        # 当area_id为 为空时，查询所有的省
        if area_id is None:
            # 使用cache缓存查询的数据，避免后面的重复查询，提示性能!!
            # 优先从缓存中获取数据
            province_list = cache.get('province_list')
            if province_list is None:
                province_qs = Area.objects.filter(parent__isnull=True)
                # QueryDict 对象不能直接作为json数据里的内容 构造响应体
                # 根据API构造响应体数据
                province_list = []
                for province in province_qs:
                    # 所以需要将单个 Area 模型对象的内容转成字典 形式
                    province_list.append({'id':province.id, 'name': province.name})
                # cache.set('key', 内容, 有效期)
                cache.set('province_list',province_list,3600)

            return http.JsonResponse({'code': RETCODE.OK,'errmsg': 'OK', 'province_list': province_list})
        # 当area_id为不为空时根据area_id查询对应的行政区
        else:
            # area_qs = Area.objects.filter(parent_id=area_id)
            # area_list = []
            # for area in area_qs:
            #     area_list.append({'id':area.id,'name':area.name})
            """优先从缓存中获取数据"""
            sub_data = cache.get('sub_%s' % area_id)
            if sub_data is None:
                try:
                    # 查询area_id对应的行政区
                    parent_qs = Area.objects.get(id=area_id)
                    # 根据area_id对应的行政区，查找下级行政区
                    area_qs = parent_qs.subs.all()
                    sub_list = []
                    for area in area_qs:
                        sub_list.append({'id':area.id,'name':area.name})
                    sub_data = {
                        'id':parent_qs.id,
                        'name':parent_qs.name,
                        'subs':sub_list
                    }
                    cache.set('sub_%s' % area_id,sub_data,3600)
                except Area.DoesNotExist:
                    return http.HttpResponseForbidden('Error area_id')
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'sub_data':sub_data})
