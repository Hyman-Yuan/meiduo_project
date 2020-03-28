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
            'selected': selected,
            'price': sku.price,
            'default_image_url': sku.default_image.url,
            'amount': sku.price * count,
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

    # 删除购物车,本质还是在修改购物车数据
    def delete(self,request):
        # 接收请求体数据（json数据）
        json_dict = json.loads(request.body.decode())
        sku_id = json_dict.get('sku_id')
        # 校验
        try:
            sku = SKU.objects.get(id=sku_id)
        except SKU.DoesNotExist:
            return http.HttpResponseForbidden('sku_id does not exist')
        # 创建响应对象，js请求，响应JsonResponse数据
        response = http.JsonResponse({'code':RETCODE.OK,'errmsg':'OK'})
        # 获取用户 User or AnonymousUser
        user = request.user
        if user.is_authenticated:
            # 登录用户操作redis中的数据
            redis_cli = get_redis_connection('carts')
            pl = redis_cli.pipeline()
            #  HDEL KEY_NAME FIELD1 .. FIELDN  删除一个或多个哈希表中的字段
            pl.hdel(f'carts_{user.id}',sku_id)
            # SREM KEY MEMBER1..MEMBERN        移除集合中一个或多个成员
            pl.srem(f'selected_[user.id',sku_id)
            pl.execute()
        else:
            # 未登录用户操作COOKIES数据  request.COOKIES.get('key')  得到字符串数据 经过解析 得到 原始数据
            carts_str = request.COOKIES.get('carts')
            # 判断有无购物车数据  str-->b'unicode' encode
            if carts_str:
                # 字符串先encode编码，在使用base64解码，最后使用pickle模块解析成dict
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
                del carts_dict[sku_id]
            else:
                return http.HttpResponseForbidden('carts does not exist')
            # 删除购物车后数据后，重新设置COOKIE存储新的购物车数据
            # 判断购物车是否为空   carts_dict={} ?
            if not carts_dict:  # 空购物车直接删除COOKIE
                response.delete_cookie('carts')
                return response
            carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()
            response.set_cookie('carts',carts_str)

        return response


class CartsSelectedAllView(View):
    def put(self,request):  # put(this.host + '/carts/selection/', {selected}   carts.js 请求内容
        # 接收
        json_dict = json.loads(request.body.decode())
        selected = json_dict.get('selected')  # True or False  全选的状态 True 表示全选，False 表示全不选
        # 校验（判断是否：非正常请求）
        if isinstance(selected,bool) is False:
            return http.HttpResponseForbidden(' error selected status')
        response = http.JsonResponse({'code': RETCODE.OK, 'errmsg': '购物车全选成功'})
        user = request.user
        if user.is_authenticated:   # 登录用户
            redis_cli = get_redis_connection('carts')
            # redis管道对象要灵活使用，常用于写入数据。如果使用redis取数据，且后面会用到，则不能使用管道
            if selected: # 全选
                car_dict = redis_cli.hgetall(f'carts_{user.id}')   # {sku_id:count,...sku_id:count}
                #  SADD KEY_NAME VALUE1..VALUEN   pl.sadd(key_name,value1,value2,value3...)
                #  *car_dict.keys() = p1,p2,p3...
                redis_cli.sadd(f'selected_{user.id}',*car_dict.keys())
            else: # 表示全不选  删除存储selected状态的set集合 selected_user.id
                redis_cli.delete(f'selected_{user.id}')
        else:  # 未登录用户
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
                # 核心思想 修改购物车每个sku_id小字典中的selected的值
                # 讲义方法
                if selected:
                    for sku_dict in carts_dict.values():
                        sku_dict['selected'] = selected
                else:
                    for sku_dict in carts_dict.values():
                        sku_dict['selected'] = selected
                # if selected:
                #     for sku_id in carts_dict.keys():
                #         carts_dict[sku_id]['selected'] = selected
                # else:
                #     for sku_id in carts_dict.keys():
                #         carts_dict[sku_id]['selected'] = selected
                carts_str = base64.b64encode(pickle.dumps(carts_dict)).decode()
                response.set_cookie('carts',carts_str)
            else:
                return http.HttpResponseForbidden('does not have carts data')
        return response


class CartsSimpleView(View):
    # GET /carts/simple/
    # js cart_skus
    def get(self,request):
        user = request.user
        if user.is_authenticated:
            redis_cli = get_redis_connection('carts')
            # 获取购物车数据
            redis_dict = redis_cli.hgetall(f'carts_{user.id}')  # carts_user.id:{sku_id:count,}
            selected_ids = redis_cli.smembers('selected_%s' % user.id)
            if not redis_dict:
                return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '没有购物车数据'})
            carts_dict = {}
            # li = redis_dict.keys()
            for sku_id_bytes in redis_dict:
                for sku_id_bytes in redis_dict:     # 实现的功能等价于for sku_id_bytes in redis_dict.keys()
                    # a = sku_id_bytes    #
                    carts_dict[int(sku_id_bytes)] = {
                        'count': int(redis_dict[sku_id_bytes]),
                        'selected': sku_id_bytes in selected_ids
                    }
        else:
            carts_str = request.COOKIES.get('carts')
            if carts_str:
                carts_dict = pickle.loads(base64.b64decode(carts_str.encode()))
            else:
                return http.JsonResponse({'code': RETCODE.NODATAERR, 'errmsg': '没有购物车数据'})
        # 查询购物车中所有sku_id对应的sku模型
        sku_qs = SKU.objects.filter(id__in=carts_dict.keys())
        # 定义一个列表用来包装所有购物车商品字典
        sku_list = []
        for sku in sku_qs:
            selected = carts_dict[sku.id]['selected']
            count = carts_dict[sku.id]['count']
            sku_list.append({
                # 注册前面bool和 Decimal类型问题注意车换成str
                'id': sku.id,
                'name': sku.name,
                'default_image_url': sku.default_image.url,
                'count': count
            })
        return http.JsonResponse({'code': RETCODE.OK, 'errmsg': 'OK', 'cart_skus': sku_list})