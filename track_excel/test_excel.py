# -*- coding: utf-8 -*-
# author:ghoti
from read_excel import Read_Excel, Export_Excel


def main():
    headings = ['no', 'date']
    values = [['12345', '2012-12-12'], ['12346', '2012-12-13']]
    Export_Excel(headings, values, file_name='a.xls')()

    r = Read_Excel(file_name='a.xls')()
    print r
    [{'no': '12345', 'date': '2012-12-12'},
     {'no': '12346', 'date': '2012-12-13'}]


if __name__ == '__main__':
    main()
