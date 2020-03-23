from django.core.files.storage import Storage


class FastDFSStorage(Storage):
    def _open(self,name, mode='rb'):
        """
        当打开某个文件时就会自动调用存方法
        :param name: 要打开的文件名
        :param mode: 打开文件的模板
        :return: 打开后的文件对象
        """
        pass

    def _save(self, name, content):
        """
        上传文件时会自动调用此方法
        :param name: 要上传的文件名
        :param content: 文件打开之后read读取出来的bytes类型
        :return: file_id
        """
        pass

    def url(self, name):
        """
        当对image字典调用url属性就会来调用此方法
        :param name: file_id
        :return: 完整的图片url : http://192.168.115.132:8888/ + file_id
        """
        return 'http://192.168.115.132:8888/' + name
