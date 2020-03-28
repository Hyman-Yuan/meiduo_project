from django.shortcuts import render
from django_redis import get_redis_connection
from decimal import Decimal

from meiduo_mall.utils.views import LoginRequiredView
from user.models import Address
from goods.models import SKU


class OrderSettlementView(LoginRequiredView):
    """结算订单"""

    def get(self, request):
        """提供订单结算页面"""
        # 获取登录用户
        user = request.user
        # 查询地址信息
        addresses = Address.objects.filter(user=user, is_deleted=False)

        # 如果地址为空，渲染模板时会判断，并跳转到地址编辑页面
        # addresses = addresses or None

        # 从Redis购物车中查询出被勾选的商品信息
        redis_conn = get_redis_connection('carts')
        redis_cart = redis_conn.hgetall('carts_%s' % user.id)
        cart_selected = redis_conn.smembers('selected_%s' % user.id)
        cart = {}  # 包装购物车中那些勾选商品的sku_id : count
        for sku_id in cart_selected:
            cart[int(sku_id)] = int(redis_cart[sku_id])

        # 准备初始值
        total_count = 0
        total_amount = Decimal('0.00')
        # 查询商品信息
        skus = SKU.objects.filter(id__in=cart.keys())
        for sku in skus:
            sku.count = cart[sku.id]
            sku.amount = sku.count * sku.price
            # 计算总数量和总金额
            total_count += sku.count
            total_amount += sku.amount
        # 补充运费
        freight = Decimal('10.00')

        # 渲染界面
        context = {
            'addresses': addresses,
            'skus': skus,
            'total_count': total_count,
            'total_amount': total_amount,
            'freight': freight,
            'payment_amount':total_amount + freight
        }

        return render(request, 'place_order.html', context)

class OrderCommitView(LoginRequiredView):
    """提交订单"""
    def post(self, request):
        # 接收请求体数据
        # 校验
        # 新增订单基本信息记录(OrderInfo) 一
        # 修改sku库存和销量
        # 修改spu销量
        # 新增订单商品信息记录(OrderGoods)  多
        # 将购物车中已提交订单的商品删除
        # 响应 order_id
        pass