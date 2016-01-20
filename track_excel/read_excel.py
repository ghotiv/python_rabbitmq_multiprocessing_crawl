# -*- coding: utf-8 -*-
# author:ghoti
import xlrd
import xlwt
import base64
import cStringIO


class Read_Excel:
    """
        根据索引获取Excel表格中的数据
        参数:file_name：Excel文件路径;file_contents:二进制文件/字符串
        col_n：表头列名所在行数 ;del_n:表的后几行不读入; by_index：表的索引（默认第一个sheet）
        返回表格中某一行作为key的字典列表,key为unicode类型
        校验:不能有重复的项,不能有空项
    """

    def __init__(self,
                 file_contents=None,
                 file_name=None,
                 col_n=1,
                 del_n=0,
                 by_index=0, ):
        self.file_name = file_name
        self.file_contents = file_contents
        self.col_n = col_n
        self.del_n = del_n
        self.by_index = by_index

    def __call__(self):
        try:
            data = xlrd.open_workbook(filename=self.file_name,
                                      file_contents=self.file_contents)
        except Exception, e:
            print str(e)
            return None
        col_n = self.col_n
        del_n = self.del_n
        by_index = self.by_index
        table = data.sheets()[by_index]
        # 行数
        nrows = table.nrows
        # 某一行数据做字典的key
        colnames = table.row_values(col_n - 1)
        # validate
        if colnames:
            repeat_colnames = set(
                [str(i) for i in colnames if colnames.count(i) != 1])
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
    """
        返回导出excel二进制数据,
        sheet_name为sheet名,headings为第一行,data为第二行后,
        2个列表headings,data的内容一一对应
    """

    def __init__(self,
                 headings,
                 data,
                 sheet_name='export_xls',
                 file_name=None):
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
        sheet.set_horz_split_pos(rowx + 1
                                 )  # in general, freeze after last heading row
        sheet.set_remove_splits(
            True)  # if user does unfreeze, don't leave a split there
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
