# -*- coding: utf-8 -*-
#author:ghoti

'''Do with tabao top.api to get data'''
import time
import top.api

class Top(object):
    '''Do with taobao top.api run the funciton like taobao.items.onsale.get
       and get the response
    '''
    def __init__(self, appkey=None, secret=None, sessionkey=None, url=None, port=None, website=None):
        self.appkey = appkey
        self.secret = secret
        self.sessionkey = sessionkey
        # self.url = 'gw.api.tbsandbox.com'  #沙箱
        self.url = 'gw.api.taobao.com'  # 正式环境
        self.port = 80
        self.total_results = 0
        if website:
            self.url = website.url
            self.appkey = website.web_app_key
            self.secret = website.web_app_secret
            self.sessionkey = website.web_session_key
           
    def __call__(self, method_name, **args):
        '''直接调用淘宝api返回数据
           tips:
               method_name = 'taobao.items.onsale.get'
               req=top.api.ItemsOnsaleGetRequest(url,port)
        '''
        api_name = ''.join([i.capitalize() for i in method_name.split('.')[1:]]) + 'Request'
        req = getattr(top.api, api_name)(self.url, self.port)
        req.set_app_info(top.appinfo(self.appkey, self.secret))
        [setattr(req, i, args[i]) for i in args]
        rsp = {}
        try:
            rsp = req.getResponse(self.sessionkey)
        except Exception, e:
            rsp['error'] = e
            return rsp
        if rsp and 'error' not in rsp:
            rsp = rsp.get(method_name.replace('.', '_')[7:] + '_response', {})
        return rsp
   
    def _top_items_onsale_get_one_page(self, search_q='', fields="outer_id,num_iid,title", page_no=1):
        '''调用淘宝接口taobao.items.onsale.get,获取正在销售商品某一页的信息
           fields defalult: outer_id:外部商品编号(sku);num_iid:淘宝商品编号
        '''
        items = []
        if search_q:
            rsp = self('taobao.items.onsale.get', q=search_q, fields=fields, page_no=page_no)
        else:
            rsp = self('taobao.items.onsale.get', fields=fields, page_no=page_no)
        if 'error' in rsp:
            return rsp
        if rsp and rsp.get('items', False): items = items + rsp['items']['item']
        total_results = int(rsp.get('total_results', '0'))
        return {'items':items, 'total_results':total_results}
   
    def _top_trades_sold_get_all(self, search_q='', fields='''
        tid,buyer_nick,receiver_name,receiver_address,receiver_city,
        receiver_district,receiver_zip,receiver_phone,receiver_mobile,
        created,modified,shipping_type,buyer_rate,received_payment,status,
        orders.num_iid,orders.title,orders.price,orders.num,orders.status,
        orders.oid,has_buyer_message,consign_time,
        '''):
        '''用淘宝接口taobao.trades.sold.get,获取订单信息,默认是3个月'''
        trades = []
        page_no = 0
        page_size = 50
        total_results = 999
        while(total_results > page_no * page_size):
            if search_q:
                rsp = self('taobao.trades.sold.get', q=search_q, fields=fields, page_no=page_no + 1, page_size=page_size)
            else:
                rsp = self('taobao.trades.sold.get', fields=fields, page_no=page_no + 1, page_size=page_size)
            if rsp and rsp.get('trades', False): trades = trades + rsp['trades']['trade']
            total_results = int(rsp.get('total_results', '0'))
            page_no += 1
            time.sleep(1 / 1000)
        self.total_results = total_results
        return {'trades':trades, 'total_results':self.total_results}
   
    def _top_item_quantity_update(self, num_iid, quantity):
        '''
            用淘宝接口taobao.item.quantity.update,改变库存数量，
            成功返回True,淘宝库存为0的时候，商品会被删除，所以库存都+1
        '''
        rsp = self('taobao.item.quantity.update', num_iid=num_iid, quantity=quantity + 1)
        if 'error' in rsp:
            return rsp
        if rsp['item']['num'] == quantity + 1:
            return True
   

     
# -*- coding: utf-8 -*-
'''
    利用xmlrpc处理openerp的数据，并发写入时连接会阻塞，所以用log_in_out
    每次操作都及时登录登出，保证每次操作都有有效
'''
import re,time,os
import xmlrpclib

username = '***' #the user
pwd = '***'      #the password of the user
dbname = '***'
host = 'http://192.168.1.117:8069'

local_path = os.path.dirname(os.path.abspath(__file__))
error_file_path = os.path.join(local_path,'error.txt')

def log_in_out(*logs,**kwlogs):
    def deco(func):
        def wrapper(*args,**kwargs):
            dbname,username,pwd,host = kwlogs['dbname'],kwlogs['username'],kwlogs['pwd'],kwlogs['host']
            sock_common = xmlrpclib.ServerProxy ('%s/xmlrpc/common'%host)
            uid = sock_common.login(dbname, username, pwd)
            sock = xmlrpclib.ServerProxy('%s/xmlrpc/object'%host)
            kwargs['sock'] = sock
            kwargs['uid'] = uid
            data = func(*args,**kwargs)
            sock_common.logout(dbname, username, pwd)
            return data
        return wrapper
    return deco

@log_in_out(dbname=dbname,username=username,pwd=pwd,host=host)
def get_list(limit=20000, date_start=None, date_end=None, sock=None, uid=None):
    '''get the list of track'''
    args = [('state','in', ('traceable','partdone','done')), ('transfer_way', 'not like', '%自取%'),
            ('transfer_way', 'not in', ('',)),'|',('track_state','not like','%成功签收%'),('track_state','=',False),]
    if date_start:
        args.insert(0, ('traceable_time', '>=', date_start),)
    if date_end:
        args.insert(0, ('traceable_time', '<=', date_end),)
    ids = sock.execute(dbname, uid, pwd, 'stock.seeed.delivery', 'search', args)
    ids = sorted(ids,reverse=True)
    fields = ['id','logistic_sn','transfer_way','track_state','traceable_time','name','saleorder_id']  #fields to read
    data = sock.execute(dbname, uid, pwd, 'stock.seeed.delivery', 'read', ids, fields)     #ids is a list of id
    check_data = [i for i in data if re.search(r'^\w+$',i['logistic_sn']) and i]
    return check_data[:limit]

@log_in_out(dbname=dbname,username=username,pwd=pwd,host=host)
def write_track(_id,values,sock=None,uid=None):
    sock.execute(dbname, uid, pwd, 'stock.seeed.delivery', 'write', _id, values)



# -*- coding: utf-8 -*-
'''读写excel操作'''
import xlrd
import xlwt
import base64
import cStringIO
class Read_Excel:
    '''
                根据索引获取Excel表格中的数据   参数:file_name：Excel文件路径;file_contents:二进制文件/字符串
       col_n：表头列名所在行数 ;del_n:表的后几行不读入; by_index：表的索引（默认第一个sheet）
                返回表格中某一行作为key的字典列表,key为unicode类型
                校验:不能有重复的项,不能有空项
    '''
    def __init__(self, file_contents=None, file_name=None, col_n=1, del_n=0, by_index=0):
        self.file_name = file_name
        self.file_contents = file_contents
        self.col_n = col_n
        self.del_n = del_n
        self.by_index = by_index

    def __call__(self):
        try:
            data = xlrd.open_workbook(filename=self.file_name, file_contents=self.file_contents)
        except Exception, e:
            print str(e)
            return None
        col_n = self.col_n
        del_n = self.del_n
        by_index = self.by_index
        table = data.sheets()[by_index]
        nrows = table.nrows  # 行数
        # ncols = table.ncols #列数
        colnames = table.row_values(col_n - 1)  # 某一行数据做字典的key
        # validate
        if colnames:
            repeat_colnames = set([str(i) for i in colnames if colnames.count(i) != 1])
            for i in colnames:
                if not i:
                    raise NameError('Null colname exist')
            if repeat_colnames:
                alert_info = ';'.join(repeat_colnames)
                raise NameError('repeat colname exist : %s' % alert_info)
        rsp = []
        for rownum in range(col_n, nrows - del_n):
            row = table.row_values(rownum)
            if row:
                app = {}
                for i in range(len(colnames)):
                    app[colnames[i].strip()] = row[i]
                rsp.append(app)
        return rsp

class Export_Excel:
    '''返回导出excel二进制数据,sheet_name为sheet名,headings为第一行,data为第二行后,2个列表的内容一一对应'''
    def __init__(self, headings, data, sheet_name='export_xls', file_name=None):
        self.sheet_name = sheet_name
        self.headings = headings
        self.data = data
        self.file_name = file_name

    def __call__(self):
        book = xlwt.Workbook()
        sheet = book.add_sheet(self.sheet_name)
        rowx = 0
        for colx, value in enumerate(self.headings):
            sheet.write(rowx, colx, value)
        sheet.set_panes_frozen(True)  # frozen headings instead of split panes
        sheet.set_horz_split_pos(rowx + 1)  # in general, freeze after last heading row
        sheet.set_remove_splits(True)  # if user does unfreeze, don't leave a split there
        for row in self.data:
            rowx += 1
            for colx, value in enumerate(row):
                sheet.write(rowx, colx, value.encode('utf-8').decode('utf-8'))
        buf = cStringIO.StringIO()
        if self.file_name:
            book.save(self.file_name)
        book.save(buf)
        out = base64.encodestring(buf.getvalue())
        buf.close()
        return out


# -*- coding: utf-8 -*-
'''自定义多线程运行函数，可定义同时运行个数'''
import threading,time
from time import sleep,ctime
class My_Thead:
    '''
            多线程运行函数，将all_list切片处理，num为进程数，all_list小于num，单线程运行，
    sleep_time为单个进程（一个all_list切片）运行后停留时间（方便调试），
    myfunc为处理每个切片的函数，对all_list切片，在处理
    '''
    def __init__ (self, all_list, num, sleep_time=0, myfunc=None):
        self.all_list = all_list
        self.len_list = len(all_list)
        self.num = num    #进程数,实际进程为可能为num+1
        if len(all_list)<num:
            self.num = 1
        self.m = self.len_list/self.num
        if not self.m:
            self.m = 1
        self.loops=range(0 , self.len_list, self.m)
        self.sleep_time = sleep_time
        self.myfunc = myfunc
    def loop (self,nloop,n,m):
        self.myfunc(n,m)
        sleep(self.sleep_time)
    def __call__ (self):
        if not self.all_list:
            return False
        threads=[]
        nloops=range(len(self.loops))
        for i in nloops:
            t=threading.Thread(target=self.loop,args=(i, self.loops[i], self.m))
            threads.append(t)
        for i in nloops:
            threads[i].start()
        for i in nloops:
            threads[i].join()


def sum_list(dict_list,compare_arg,sum_arg):
    from itertools import groupby
    def compare(i):
        return [ i[j] for j in compare_arg ]
    def func_one(x,y):
        for i in sum_arg:
            x[i]=x[i]+y[i]
        return x
    return [reduce(func_one,k) for i, k in groupby(dict_list, compare)]

a = [
     {1:2,3:2,5:2,6:1,7:3,8:1},
     {1:2,3:2,5:2,6:2,7:2,8:2},
     {1:2,3:2,5:2,6:3,7:2,8:3},
     {1:3,3:2,5:2,6:3,7:2,8:6},
     {1:3,3:2,5:2,6:3,7:2,8:9},
     ]
print sum_list(a,[1,3,5],[6,7])

#result
#[{1: 2, 3: 2, 5: 2, 6: 6.0, 7: 7.0, 8: 1}, {1: 3, 3: 2, 5: 2, 6: 6.0, 7: 4.0, 8: 6}]

#use setdefault
b = (1,2),(1,3),(1,5),(2,6)
c = {}
for i in b:
    c.setdefault(i[0],[]).append(i[1])
#result c
#{1: [2, 3, 5], 2: [6]}

## dict_add
from itertools import groupby,chain
a = [{'a':1,'s':5},{'a':2,'s':5},{'a':5,'s':5}]
b = [{'a':1,'p':5},{'a':3,'p':5},{'a':5,'p':5}]
c = [{'a':2,'t':5},{'a':3,'t':5},{'a':6,'t':5}]
print [reduce(lambda x,y: dict(x,**y),k) for i,k in groupby(sorted(chain(a+b+c),key=lambda x:x['a']),lambda x:x['a'])]
#[{'a': 1, 'p': 5, 's': 5}, {'a': 2, 's': 5, 't': 5}, {'a': 3, 'p': 5, 't': 5}, {'a': 5, 'p': 5, 's': 5}, {'a': 6, 't': 5}]

## left join
from itertools import groupby,chain
l1 = [{"a":1, "b":2,'d':1}, {"a":2, "b":3, 'd':6}, {"a":1, "b":3, 'd':5}]
l2 = [{"a":1, 'b':2, "c":4}, {"a":2,'b':3,"c":3},{"a":5,'b':2,"c":5}]
l3 = [{"a":2, 'b':4, "c":4}, {"a":2,'b':3,"c":3},{"a":5,'b':2,"c":5}]
lia = [reduce(lambda x,y: dict(x,**y),k) for i,k in\
groupby(sorted(chain(l1,l2,l3),key=lambda x:(x.get('a',None),x.get('b',None))),lambda x:(x.get('a',None),x.get('b',None)))\
if i in [m for m,n in groupby(sorted(l1),lambda x:(x['a'],x['b']))]
]
#print lia
#[{'a': 1, 'c': 4, 'b': 2, 'd': 1}, {'a': 1, 'b': 3, 'd': 5}, {'a': 2, 'c': 3, 'b': 3, 'd': 6}]
