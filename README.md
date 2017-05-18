# python_rabbitmq_multiprocessing_crawl

to get the intenational logistics information

### main skills

    rabbitmq,casperjs,multiprocessing,requests,python
    
### advantages

    1.distributed crawler
    2.casperjs can get the webpage load with js
    3.multiprocessing can use the Multi core CPU 

### motive

    The project can be used in openerp (database: postgresql) with xmlrpc first
    To use in general, alter it with excel

### install

    #test on ubuntu 14.04
    #casperjs 1.1.0 phantomjs 1.9.0
    sudo apt-eget install phantomjs
    $ git clone git://github.com/n1k0/casperjs.git
    $ cd casperjs
    $ ln -sf `pwd`/bin/casperjs /usr/local/bin/casperjs
    sudo pip install xlrd,xlwt,requests
    sudo apt-get install rabbitmq-server

### usage

    1.python receive_data.py  rabbitmq consumer,receive and do the data，can function on multi computer
    2.python send_data.py  rabbitmq producer,read the logistics number and put to list
    3.python save_to_excel.py reand success_data_***.txt and save to track_result.xls

### modles
	
    receive_data.py :  rabbitmq consumer,receive and do the data，can function on multi computer
    send_data.py    ： rabbitmq producer,read the logistics number and put to list
    save_to_excel.py : reand success_data_***.txt and save to track_result.xls
    my_rabbitmq.py  ： rabbitmq main function,send and receive data
    do_track.py     : use requests and casperjs to get the webpage,and parse, use multiprocessing
    track_data.py   ： basic variable,read and write excel
    my_process_pool.py :  record multiprocessing exception
    read_excel.py      :  read and write excel
    track.js           :  capsperjs ues it to get webpage
    rpc_api.py         :  xmlrpc api do with openerp
    ftp_up.py          :  ftp up json file to php server
    test_excel.py      :  test excel function
    some_code.py       :  some code
	

### some file

      sample_import.xls      excel about logistics number
      error_data_***.txt     error message
      success_data_***.txt   success message
      track_***.log          track log

### to do

      can use with the websiete,datebae:redis,mongodb and so on
      import excel about logistics number and export excel about logistics detail
