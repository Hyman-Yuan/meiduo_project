from django.db import models

# Create your models here.

#  继承父类 模型,添加创建日期.更新日期 字段
class BaseModels(models.Model):

    create_time = models.TimeField(auto_now_add=True,verbose_name='创建时间')
    update_time = models.TimeField(auto_now=True,verbose_name='更新时间')

    # Django模型类的Meta是一个内部类，它用于定义一些Django模型类的行为特性。
    class Meta:
        # 定义当前的模型是不是一个抽象类。
        # 所谓抽象类是不会对应数据库表的。一般我们用它来归纳一些公共属性字段，然后继承它的子类可以继承这些字段。
        abstract = True
