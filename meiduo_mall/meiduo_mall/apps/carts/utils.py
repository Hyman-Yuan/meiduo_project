import pickle, base64
from django_redis import get_redis_connection


def merge_cart_cookie_to_redis(request, response):

    # 1.先获取cookie购物车数据
    cart_str = request.COOKIES.get('carts')
    if cart_str is None:
        # 判断是否有cookie购物车数据,如果没有提前return
        return

    # 如果有购物车数据 cart_str --> cart_dict
    cart_dict = pickle.loads(base64.b64decode(cart_str.encode()))
    # 创建redis连接对象
    redis_cli = get_redis_connection('carts')
    pl = redis_cli.pipeline()
    user = request.user # 只有状态保持之后 请求中的user才不会是匿名用户
    # 遍历cart_dict 将cookie购物车数据向redis购物车添加
    for sku_id in cart_dict:
        pl.hset('cart_%s' % user.id, sku_id, cart_dict[sku_id]['count'])
        # 判断当前cookie购物车商品是否勾选,如果勾选将sku_id添加到set中
        if cart_dict[sku_id]['selected']:
            pl.sadd('selected_%s' % user.id, sku_id)
        else:
            pl.srem('selected_%s' % user.id, sku_id)
    pl.execute()

    # 合并完成将cookie购物车数据删除
    response.delete_cookie('carts')

