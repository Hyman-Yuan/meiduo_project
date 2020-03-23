from django.shortcuts import render
from django.views import View
from django import http
# Create your views here.
from contents.utils import get_goods_categories
from .models import GoodsCategory
from .utils import category_navication

class ListView(View):
    def get(self,request,category_id,page_num):
        try:
            cats3 = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('Does not find GoodsCategory object')

        # 查询当前三级类别下的所有sku
        sku_qs = cats3.sku_set.filter(is_launched=True)
        # 查询到当前所有数据，如果直接返回前端，渲染html 影响查询性能，同时前端数据 过多
        # 每页展示的数量
        page = 3
        # 当前三级类别下sku总数量
        sku_count = sku_qs.count()
        # 需要分页的数量
        page_num = int(page_num)
        total_pages = sku_count // page + 1 if (sku_count % page) else 0
        start = (page_num-1) * page
        end = start + page
        page_skus = sku_qs[start:end]

        data ={
            'categories':get_goods_categories(),    # 商品类型
            'breadcrumb':category_navication(cats3),                        # 面包屑数据
            'category': cats3,  # 三级类型模型对象
            'sort': 'price',  # 排序字段
            'page_skus': page_skus,  # 当前页要展示的所有sku数据
            'page_num': page_num,  # 当前显示第几页
            'total_page': total_pages,  # 总页数
        }

        return render(request,'list.html',data)
        pass