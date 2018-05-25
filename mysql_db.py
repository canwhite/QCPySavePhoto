#游标
import pymysql.cursors
#os模块
import os
#操作配置文件
import configparser as cparser
from PIL import Image
import sys




base_dir = str(os.getcwd())

#将地址'\'转化为反斜杠“／”,windows到mac的转换
base_dir = base_dir.replace("\\","/")


#拼接出服务器配置文件的路径
file_path = base_dir + "/picture_config.ini"

#配置文件操作
cf = cparser.ConfigParser()

#读取配置文件的内容
cf.read(file_path)

host = cf.get("mysqlconf","host")
port = cf.get("mysqlconf","port")
db = cf.get("mysqlconf","db_name")
user = cf.get("mysqlconf","user")
password = cf.get("mysqlconf","password")


class DB:
    def __init__(self):
        try:
            #建立链接
            self.connection = pymysql.connect(host = host,
                                              port = int(port),
                                              user = user,
                                              password = password,
                                              db = db,
                                              charset = 'utf8mb4',
                                              cursorclass= pymysql.cursors.DictCursor)

        except pymysql.err.OperationalError as e:

            print("Mysql Error %d:%s" %(e.args[0],e.args[1]))

    def clear(self, table_name):

        # real_sql = "truncate table " + table_name + ";"
        #创建一条sql语句，删除表中所有内容
        real_sql = "delete from " + table_name + ";"
        #去掉外键限制，并执行清除语句
        with self.connection.cursor() as cursor:

            cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            #执行上面那个不需要参数的sql语句，删除表数据
            cursor.execute(real_sql)
        #往服务器提交一下操作
        self.connection.commit()


    def close(self):
        self.connection.close();

    # 插入语句
    def insert(self, table_name, table_data):

        #因为我们执行的是字符串，所以把table_data中的数据提取出来拼接一下
        #把value转化成字符串并重新存储

        for key in table_data:
            table_data[key] = "'"+str(table_data[key])+"'"
        #join
        #语法：  'sep'.join(list)
        # sep：分隔符。可以为空
        # list：要连接的元素序列、字符串、元组、字典

        key   = ','.join(table_data.keys())
        value = ','.join(table_data.values())

        #再写sql字段
        real_sql = "INSERT INTO " + table_name + " (" + key + ") VALUES (" + value + ")"
        print(real_sql)

        with self.connection.cursor() as cursor:
            #执行sql语句
            cursor.execute(real_sql)
        #操作提交一下
        self.connection.commit()



    #因为blob要求为64kb，如果图片过大，压缩，需要模块pillow

    def compress_picture(self,image_dir):
        #先显示一下吧
        im = Image.open(image_dir)
        #查看视图的大小
        width,height = im.size;
        print("width:" + str(width));
        print("height:" + str(height));

        #重新构建大小
        resizedIm = im.resize((int(width/3), int(height/3)))

        #保存到本地,重复执行只构建一个
        resizedIm.save(base_dir + "/resize.jpg")

        #重新查看
        width,height = resizedIm.size;
        print("new_width:" + str(width));
        print("new_height:" + str(height));


if __name__ == '__main__':

    print(base_dir);

    db = DB()
    image_dir = base_dir + "/test.jpg"
    # db.compress_picture(image_dir);
    #自己要写入的表的名字
    table_name = "my_photo"

    #插入数据
    data = {'id':1,'name':'zack','photo':image_dir};
    db.clear(table_name)
    db.insert(table_name,data)
    db.close()












