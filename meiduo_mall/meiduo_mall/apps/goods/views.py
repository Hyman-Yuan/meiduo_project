from django.shortcuts import render
from django.views import View
from django import http
from django.core.paginator import Paginator, EmptyPage
from django.utils import timezone
# Create your views here.
from meiduo_mall.utils.response_code import RETCODE
from contents.utils import get_goods_categories
from .models import GoodsCategory, SKU, GoodsVisitCount
from .utils import category_navication


class ListView(View):
    def get(self, request, category_id, page_num):
        try:
            cats3 = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('Does not find GoodsCategory object')
        # 商品列表排序(price:price)(hot:sales)(default:create_time/update_time)
        sort = request.GET.get('sort')
        if sort == 'price':
            sort_field = 'price'
        elif sort == 'hot':
            sort_field = 'sales'
        else:
            sort = 'default'
            sort_field = 'create_time'

        # 查询当前三级类别下的所有sku
        sku_qs = cats3.sku_set.filter(is_launched=True).order_by(sort_field)
        # 查询到当前所有数据，如果直接返回前端，渲染html 影响查询性能，同时前端数据 过多
        # 每页展示的数量
        page = 3
        page_num = int(page_num)
        '''
        # 当前三级类别下sku总数量
        sku_count = sku_qs.count()
        # 需要分页的数量
        total_pages = sku_count // page + 1 if (sku_count % page) else 0
        start = (page_num-1) * page
        end = start + page
        # 获取指定页的数据
        page_skus = sku_qs[start:end]
        '''
        # 使用分页器 Paginator 创建分页器对象 实现分页
        paginator = Paginator(sku_qs, page)
        # 需要分页的数量
        total_pages = paginator.num_pages
        # 获取指定页的数据
        try:
            page_skus = paginator.page(page_num)
        except EmptyPage:
            return http.HttpResponseForbidden('the page does noe exist')

        data = {
            'categories': get_goods_categories(),  # 商品类型
            'breadcrumb': category_navication(cats3),  # 面包屑数据
            'category': cats3,  # 三级类型模型对象
            'sort': sort,  # 排序字段
            'page_skus': page_skus,  # 当前页要展示的所有sku数据
            'page_num': page_num,  # 当前显示第几页
            'total_page': total_pages,  # 总页数
        }

        return render(request, 'list.html', data)


# /hot/115/
class HotGoodsView(View):
    def get(self, request, category_id):
        try:
            cats3 = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden(f'id:{category_id} does not exit')
        # 按销量降序排列商品,并获取销量最大的两个商品
        sku_qs = cats3.sku_set.filter(is_launched=True).order_by('-sales')[:2]
        sku_list = []
        for sku in sku_qs:
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'price': sku.price,
                'default_image_url': sku.default_image.url
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'hot_skus': sku_list})


#         sku_qs = cat3.sku_set.filter(is_launched=True).order_by('-sales')[:2]
#         # 将sku查询集中的模型转字典并添加到列表中
#         sku_list = []  # 用来包装sku字典
#         for sku in sku_qs:
#             sku_list.append({
#                 'id': sku.id,
#                 'name': sku.name,
#                 'price': sku.price,
#                 'default_image_url': sku.default_image.url
#             })

# /detail/3/

class DetailView(View):
    def get(self, request, sku_id):
        try:
            sku = SKU.objects.get(id=sku_id, is_launched=True)
            cats3 = sku.category
            spu = sku.spu
        except SKU.DoesNotExist:
            return render(request, '404.html')
        # 获取规格型号
        """1.准备当前商品的规格选项列表 [8, 11]"""
        # 获取出当前正显示的sku商品的规格选项id列表
        current_sku_spec_qs = sku.specs.order_by('spec_id')
        current_sku_option_ids = []  # [8, 11]
        for current_sku_spec in current_sku_spec_qs:
            current_sku_option_ids.append(current_sku_spec.option_id)

        """2.构造规格选择仓库
        {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        """
        # 构造规格选择仓库
        temp_sku_qs = spu.sku_set.all()  # 获取当前spu下的所有sku
        # 选项仓库大字典
        spec_sku_map = {}  # {(8, 11): 3, (8, 12): 4, (9, 11): 5, (9, 12): 6, (10, 11): 7, (10, 12): 8}
        for temp_sku in temp_sku_qs:
            # 查询每一个sku的规格数据
            temp_spec_qs = temp_sku.specs.order_by('spec_id')
            temp_sku_option_ids = []  # 用来包装每个sku的选项值
            for temp_spec in temp_spec_qs:
                temp_sku_option_ids.append(temp_spec.option_id)
            spec_sku_map[tuple(temp_sku_option_ids)] = temp_sku.id

        """3.组合 并找到sku_id 绑定"""
        spu_spec_qs = spu.specs.order_by('id')  # 获取当前spu中的所有规格

        for index, spec in enumerate(spu_spec_qs):  # 遍历当前所有的规格
            spec_option_qs = spec.options.all()  # 获取当前规格中的所有选项
            temp_option_ids = current_sku_option_ids[:]  # 复制一个新的当前显示商品的规格选项列表
            for option in spec_option_qs:  # 遍历当前规格下的所有选项
                temp_option_ids[index] = option.id  # [8, 12]
                option.sku_id = spec_sku_map.get(tuple(temp_option_ids))  # 给每个选项对象绑定下他sku_id属性

            spec.spec_options = spec_option_qs  # 把规格下的所有选项绑定到规格对象的spec_options属性上

        context = {
            'categories': get_goods_categories(),  # 商品分类
            'breadcrumb': category_navication(cats3),  # 面包屑导航
            'sku': sku,  # 当前要显示的sku模型对象
            'category': cats3,  # 当前的显示sku所属的三级类别
            'spu': spu,  # sku所属的spu
            'spec_qs': spu_spec_qs,  # 当前商品的所有规格数据
        }

        return render(request, 'detail.html', context)


class VisitView(View):
    def post(self, request, category_id):
        # 1.获取当前category_id 的模型对象
        try:
            category = GoodsCategory.objects.get(id=category_id)
        except GoodsCategory.DoesNotExist:
            return http.HttpResponseForbidden('Not found category_id')
        # 获取当天日期
        today_date = timezone.now()
        # 2.判断当天是否访问过此类别的商品，没有则新增，有则count+1
        try:
            goods_visits = GoodsVisitCount.objects.get(category=category,date=today_date)
        except GoodsVisitCount.DoesNotExist:
            goods_visits = GoodsVisitCount(category=category,date=today_date)
        goods_visits.count += 1      # 增加访问量
        goods_visits.save()
        return http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})
