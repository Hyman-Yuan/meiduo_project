# 1. 导入FastDFS客户端扩展
from fdfs_client.client import Fdfs_client
import os
# 2. 创建FastDFS客户端实例
# 文件批量导入 storage
def save_file_to_storage(file_dir):
    client = Fdfs_client('client.conf')
    # 3. 调用FastDFS客户端上传文件方法
    # client.upload_appender_by_filename()
    file_list = file_name(file_dir)
    try:
        for file in file_list:
            ret = client.upload_by_filename(file_dir + f'/{file}')
    except:
        print('error')
    # ret = client.upload_by_filename('/home/python/Desktop/fastdfs_log/test_image/01.jpeg')
# 批量获取文件名
def file_name(file_dir):
    for root, dirs, files in os.walk(file_dir):
        # print(root)     # get path
        # print(dirs)     # get all sub_dirs
        # print(type(files[0]))  # get all files (not dirs)
        return files

if __name__ == '__main__':
    pass
    # file_name('/home/python/Desktop/fastdfs_log/test_image')
    # save_file_to_storage('/home/python/Desktop/fastdfs_log/test_image')
