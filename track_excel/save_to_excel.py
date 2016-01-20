#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
@author: ghoti
"""
from track_data import write_list, SUCCESS_DATA_PATH, SAVE_EXCEL_PATH


def main():
    write_list(SUCCESS_DATA_PATH, SAVE_EXCEL_PATH)


if __name__ == '__main__':
    main()
