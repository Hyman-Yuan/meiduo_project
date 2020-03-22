
from goods.models import GoodsChannel
from contents.models import ContentCategory

# 商品类别展示函数
def get_goods_categories():
    ''' 需要传递给前端的数据  结构
    categories = {
        # categories 中的键值对数量是动态的，取决于GoodsChannelGroup模型中 模型的数量
        'group_id1':{'channels':[],'sub_cats':[]},
        ...
        'group_id2':{'channels':[],'sub_cats':[]},
        ...
        'group_idn':{'channels':[],'sub_cats':[]},
    }
    group_id : 商品频道分组  取决于商品的 GoodsChannel模型中 group_id字段,   商品频道分组
    channels : 当前商品频道对应的  一级类别  模型对象  的存放容器
    sub_cats :
    '''

    # 1.定义一个变量用来包装所有商品类别数据字典
    # categories = {}
    # 2.查询所有的GoodsChannel(商品频道)模型对象,根据group_id,sequence字段进行排序
    # goods_channel_qs = GoodsChannel.objects.order_by('group_id', 'sequence')
    # 3,使用for循环遍历所有模型对象，并对categories的内层进行包装
    # for goods_channel in goods_channel_qs:
    # 4.获取当前模型的group_id(频道分组)字段
    #     group_id = goods_channel.group_id
    # 5.判断categories中group_id的键是否存在，存在则跳过，不存在则新增group_id
    #     categories.setdefault(group_id, {'channels': [], 'sub_cats': []})
    # 6.通过商品频道查询对应的 一级类别 对象
    #     GoodsCategory 自关联模型 （id name parent(subs)）
    #     cat = goods_channel.category
    # 7.将查询到的一级类别模型对象添加到当前group_id的channels列表中
    #     categories[group_id]['channels'].append(cat)
    # 8.对数据进行包装传递到html中进行渲染
    # 前端获取本次传递的数据时 要context中使用对应的键名
    # context = {
    #     'categories': categories,
    # }
    return_data = {}
    goods_channel_qs = GoodsChannel.objects.order_by('group_id', 'sequence')
    for goods_channel in goods_channel_qs:
        group_id = goods_channel.group_id
        if group_id not in return_data:
            return_data[group_id] = {'channels': [], 'sub_cats': []}
        cat1 = goods_channel.category
        return_data[group_id]['channels'].append(cat1)
        # cat2_qs = cat.subs.all()
        # for cat2 in cat2_qs:
        #     cat3_qs = cat2.subs.all()
        #     cat2.sub_cat = cat3_qs
        #     return_data[group_id]['sub_cats'].append(cat2)
        # 通过一级类 查询当前cat1 对应的所有 二级类
        category2_qs = cat1.subs.all()
        # 遍历 二级类
        for category2 in category2_qs:
            # 获取每一个二级类 对应的三级类 的查询集
            category3_qs = category2.subs.all()
            # 将三级类 所对应的查询集 绑定到二级类的一个新增属性上 再包装到要返回的数据中
            category2.sub_cats = category3_qs
            return_data[group_id]['sub_cats'].append(category2)

    return return_data

# 广告展示函数
def show_advertisement():
    """
    {
        'index_lb': ['lb'],  # 一个列表代表同一类型的所有广告
        'index_kx': ['kx']
    }
    """
    # # 1.定义用来包装所有广告数据的大字典
    # contents = {}
    # # 2. 将所有广告类别数据全部获取到
    # content_cat_qs = ContentCategory.objects.all()
    # # 3. 遍历广告类别模型
    # for content_cat_model in content_cat_qs:
    #     # 4.包装广告数据
    #     contents[content_cat_model.key] = content_cat_model.content_set.filter(status=True).order_by('sequence')
    advertisement = {}
    adv_type_qs = ContentCategory.objects.filter()
    # class ContentCategory(BaseModels):
    #     """广告内容类别"""
    #     name = models.CharField(max_length=50, verbose_name='名称')
    #     key = models.CharField(max_length=50, verbose_name='类别键名')
    for adv_type in adv_type_qs:
        advertisement[adv_type.key] = adv_type.content_set.filter(status=True).order_by('sequence')
    return advertisement
