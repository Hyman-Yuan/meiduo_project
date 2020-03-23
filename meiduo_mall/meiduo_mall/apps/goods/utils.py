
# breadcrumb 生成面包屑数据   商品种类三级导航  level1> level2 > level3
def category_navication(subs_category):
    try:
        cats2 = subs_category.parent
        cats1 = cats2.parent
    except Exception:
        return None
    cats1.url = cats1.goodschannel_set.all()[0].url
    breadcrumb = {
        'cat1': cats1,
        'cat2': cats2,
        'cat3': subs_category,
    }
    return breadcrumb