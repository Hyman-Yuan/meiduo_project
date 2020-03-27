from django.shortcuts import render
from django.views import View
from django import http
from django_redis import get_redis_connection
import json, logging, pickle, base64
# Create your views here.
from meiduo_mall.utils.response_code import RETCODE
from goods.models import SKU

logger = logging.getLogger('django')

# Add carts
class CartsView(View):
    # 添加购物车 POST /carts/
    def post(self, request):
        # 接收数据
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')        # js传入
        count = json_dict.get('count')          # js传入
        # 提前定义一个selected变量，方便使用，无论前端是否传入了selected数据
        selected = json_dict.get('selected', True)
        # 校验
        if all([sku_id, count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id, is_launched=True)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id does not exist')
        try:
            count = int(count)
        except Exception as e:
            logger.error('error count')
            return http.HttpResponseForbidden('error count')
        if isinstance(selected, bool) is False:
            return http.HttpResponseForbidden('selected类型有误')

        user = request.user
        if user.is_authenticated:
            # 登录用户存储购物车数据到redis
            """
            hash: {sku_id_1: 1, sku_id_2: 2}
            set: {sku_id_1}
            """
            pl = get_redis_connection('carts').pipeline()
            # 将sku_id和count 向hash里面存储
            # redis_cli.hincrby(key, field, values)
            # Redis Hincrby 命令用于为哈希表中的字段值加上指定增量值。
            # HINCRBY KEY_NAME FIELD_NAME INCR_BY_NUMBER
            pl.hincrby(f"carts_{user.id}", sku_id, count)
            if selected:
                pl.sadd(f"selected_{user.id}", sku_id)
            pl.execute()
            return http.JsonResponse({'code': RETCODE.OK, 'errmsg': '添加购物车成功'})
        else:
            # 未登录用户购物车数据存入cookie
            # 2. 尝试先获取cookie购物车数据
            car_str = request.COOKIES.get('carts')
            # 判断从cookie中获取购物车数据是否为空
            # 不为空则获取到当前购物车数据
            if car_str:
                car_str_bytes = car_str.encode()
                car_unicode_bytes = base64.b64decode(car_str_bytes)
                carts_data = pickle.loads(car_unicode_bytes)
                # 判断购物车中是否存在当前sku_id,存在则count+1
                if sku_id in carts_data:
                    # origin_count = carts_data[sku_id]['count']
                    count += carts_data[sku_id]['count']
            # 否则就新创建一个购物车
            else:
                carts_data = {}
            # 重新生成购物车数据
            # 已存在sku_id count新值覆盖旧值
            # 不存在sku_id carts_data插入新的sku_id 和对应数据
            carts_data[sku_id] = {'count': count, 'selected': selected}

            car_unicode_bytes = pickle.dumps(carts_data)             # dict  --->  b'unicode'
            car_str_bytes = base64.b64encode(car_unicode_bytes)     # b'unicode' ---> b'str'
            car_str =  car_str_bytes.decode()                       # b'str' ---> 'str'
            # cat_str = base64.b64encode(pickle.dump(carts_data)).decode()
            response = http.JsonResponse({'code':RETCODE.OK,'errmsg':'添加购物车成功'})
            response.set_cookie('carts',car_str,max_age=None)
            return response

    # 展示购物车
    def get(self,request):
        user = request.user
        # 登录用户
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            redis_dict = redis_cli.hgetall(f'carts_{user.id}')
            # print(type(redis_dict))
            if not redis_dict:
                return render(request,'cart.html')
            selected_list = redis_cli.smembers(f'selected_{user.id}')
            # print(type(selected_list))
            # 将redis购物车数据格式转换成和cookie一样的大字典格式,目的:查询及包装模板需要的数据代码共享
            # 定义一个字典用来包装购物车数据 carts_data[sku_id] = {'count': count, 'selected': selected}
            carts_data = {}
            for sku_id_bytes in redis_dict:
                carts_data[int(sku_id_bytes)]={
                    'count':int(redis_dict[sku_id_bytes]),
                    'selected':sku_id_bytes in selected_list
                }
        # 未登录用户
        else:
            car_str = request.COOKIES.get('carts')
            if car_str:
                car_str_bytes = car_str.encode()    # str--->b'str'
                car_unicode_bytes = base64.b64decode(car_str_bytes)     # b'str'--->b'unicode'
                carts_data = pickle.loads(car_unicode_bytes)
            else:
                return render(request,'cart.html')
            # cat_str = base64.b64encode(pickle.dump(carts_data)).decode()
            # carts_data = pickle.loads(base64.decode(car_str.encode()))
        # 构建 render模板渲染 需要的数据
        # 根据购物车里的sku_id值，获取sku查询集
        sku_qs = SKU.objects.filter(id__in=carts_data.keys())
        sku_list = []
        for sku in sku_qs:
            selected = carts_data[sku.id]['selected']
            count = carts_data[sku.id]['count']
            sku_list.append({
                'id': sku.id,
                'name': sku.name,
                'selected': str(selected),
                'price': str(sku.price),
                'default_image_url': sku.default_image.url,
                'amount': str(sku.price * count),
                'count': count
            })
        context ={'cart_skus': sku_list}

        return render(request,'cart.html',context)
    # 修改购物车  (登录和为登录分别响应)
    '''
    def put(self,request):
        # 接收数据
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        # 提前定义一个selected变量，方便使用，无论前端是否传入了selected数据
        selected = json_dict.get('selected', True)
        # 校验
        if all([sku_id, count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id, is_launched=True)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id does not exist')
        try:
            count = int(count)
        except Exception as e:
            logger.error('error count')
            return http.HttpResponseForbidden('error count')
        if isinstance(selected, bool) is False:
            return http.HttpResponseForbidden('selected类型有误')
        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            pl = redis_cli.pipeline()
            ## 修改hash中商品count
            pl.hset(f'catrs_{user.id}',sku_id,count)
            if selected:
                pl.sadd(f'selected_{user.id}',sku_id)
            else:
                pl.srem(f'selected_{user.id}',sku_id)
            pl.execute()
            cart_sku = {
                'id': sku.id,
                'name': sku.name,
                'selected': str(selected),
                'price': str(sku.price),
                'default_image_url': sku.default_image.url,
                'amount': str(sku.price * count),
                'count': count
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            return response
        else:
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_data = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                return http.HttpResponseForbidden('没有cookie购物车数据')
            # 修改 每次请求只有一个值，请求与响应同步
            # 直接用新数据覆盖旧数据
            carts_data[sku_id]={'count':count,'selected':selected}
            # 购物车数据存入cookie
            carts_str =base64.b64encode(pickle.dumps(carts_data)).decode()
            cart_sku = {
                'id': sku.id,
                'name': sku.name,
                'selected': str(selected),
                'price': str(sku.price),
                'default_image_url': sku.default_image.url,
                'amount': str(sku.price * count),
                'count': count
            }
            response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})
            response.set_cookie('carts', carts_str)
            return response
        '''

    # 修改购物车  (功能优化): 核心思想:将前端传入的数据再返给前端，同时存储新的购物车
    def put(self, request):
        # 接收数据
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        count = json_dict.get('count')
        # 提前定义一个selected变量，方便使用，无论前端是否传入了selected数据
        selected = json_dict.get('selected', True)
        # 校验
        if all([sku_id, count]) is False:
            return http.HttpResponseForbidden('缺少必传参数')
        try:
            sku = SKU.objects.get(id=sku_id, is_launched=True)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id does not exist')
        try:
            count = int(count)
        except Exception as e:
            logger.error('error count')
            return http.HttpResponseForbidden('error count')
        if isinstance(selected, bool) is False:
            return http.HttpResponseForbidden('selected类型有误')
        # 提前构造响应数据
        cart_sku = {
            'id': sku.id,
            'name': sku.name,
            'selected': str(selected),
            'price': str(sku.price),
            'default_image_url': sku.default_image.url,
            'amount': str(sku.price * count),
            'count': count
        }
        # 创建响应对象
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '修改购物车成功', 'cart_sku': cart_sku})

        # 判断用户登录状态，实现购物车数据的存储
        # 修改逻辑： 获取购旧的物车数据，新值覆盖旧值。
        user = request.user
        if user.is_authenticated:
            # 登录用户存入redis
            redis_cli = get_redis_connection('carts')
            pl = redis_cli.pipeline()
            # 修改hash中商品count
            pl.hset(f'catrs_{user.id}', sku_id, count)
            if selected:
                pl.sadd(f'selected_{user.id}', sku_id)
            else:
                pl.srem(f'selected_{user.id}', sku_id)
            pl.execute()
        else:
            # 未登录用户存入cookie
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_data = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                return http.HttpResponseForbidden('没有cookie购物车数据')
            # 修改 每次请求只有一个值，请求与响应同步
            # 直接用新数据覆盖旧数据
            carts_data[sku_id] = {'count': count, 'selected': selected}
            # 购物车数据存入cookie
            carts_str = base64.b64encode(pickle.dumps(carts_data)).decode()
            response.set_cookie('carts', carts_str)
        return response



