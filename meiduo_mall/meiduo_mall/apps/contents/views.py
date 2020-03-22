from django.shortcuts import render
# Create your views here.
from django.views import View
from .utils import get_goods_categories

from goods.models import GoodsCategory, GoodsChannel


class IndexView(View):
    """首页"""

    def get(self, request):
        context = {'goods_categories': get_goods_categories(), # 个人写法
                   'categories':get_goods_categories()}  # 讲义写法
        return render(request, 'index.html', context)
