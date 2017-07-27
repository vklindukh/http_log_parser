## ABOUT

http_log_parser.py is designed to parse Apache HTTPd log file and extract following information

  - Top 10 requested pages and the number of requests made for each ```-s top10```
  - Percentage of successful requests ```-s success```
  - Percentage of unsuccessful requests ```-s unsuccess```
  - Top 10 unsuccessful page requests and the number of requests made for each ```-s top10unsuccess)```
  - The top 10 IPs making the most requests, and the top 5 pages requested by such IPs ```-s top10ips)```
  - The total number of requests made every minute ```-s timestat```


## DESCRIPTION

The http_log_parser.py
- reads lines from log file
- parses it using python ```re`` lib
- extracts desired statistics (according to ```-s``` option)
- display plain text report

Script uses standard ```argparse``` lib to parse command line arguments.

There are 2 classes:
- class Options(object) which parses command line options
- class Parser(object) which performs all tasks: parse string, extract metrics, calculate and display final results

Parser class keeps current statistic information in several objects:
    Parser.counter['total'] - total requests counter
    Parser.counter['success'] - successful requests counter
    Parser.counter['unsuccess']  - unsuccessful requests counter
    Parser.counter['url'] - dictionary which contents URL's (key) with counters (value)
    Parser.counter['urlunsuccess'] - dictionary which contents only unsuccessful (nont 2xx/3xx) URL's with counters
    Parser.counter['ips'] - dictionary which contents client IP's (key) with counters (value)
    Parser.counter['ippages'] - dictionary which contents list of IPs with nested dictionaries (URL's with counters)
    Parser.counter['timestat'] = dictionary which contents date's , with seconds removed, (key)
                                 with number of requests (value)

to display it use ```Parser.print_stat()```

The http_log_parser.py could prepare one or more (or all) statistics in time. You can specify the list of desired
statistics using command line option ```-s``` (with comma separated list), for example
```http_log_parser.py -f <PATH_TO_FILE> -s top10,success,success``` to get top 10 requested pages & Percentages

To get all possible statistics just omit the ```-s``` option (or set option to
```-s top10,success,unsuccess,top10unsuccess,top10ips,timestat```

Additionally you may or may not strip query string parameter from the URL. The default behavior is to remove query string.

The http_log_parser.py comes with test_http_log_parser.py which contents unit tests, see examples below.

Feel free to find all the sources on GitHub https://github.com/vklindukh/http_log_parser


## USAGE
- Get all possible options:
```
./http_log_parser.py  -h
usage: http_log_parser.py [-h] -f FILE [-s STATISTICS] [-q]

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  apache access log to process
  -s STATISTICS, --statistics STATISTICS
                        list of comma separated statistics to be calculated.
                        Default is top10,success,unsuccess,top10unsuccess,top1
                        0ips,timestat
  -q                    include query string into URL. Strip by default
```

- Extract Top 10 requested pages
```
./http_log_parser.py  -f ../apache-httpd.log -s top10

* Top 10 requested pages (page - total requests):

/printer/remove.php                                 1627
/printer/search.php                                 1581
/printer/request.php                                1559
/system/add.php                                     1544
/main/add.php                                       1542
/main/list.php                                      1542
/system/call.php                                    1542
/finance/call.php                                   1538
/statistics/list.php                                1537
/kernel/set.php                                     1536
```

- Extract Top 10 IPs making the most requests without striping query string from URL
```
./http_log_parser.py  -f ../apache-httpd.log -s top10ips -q

* Top 10 IPs making the most requests (ip - total requests) with top 10 requested pages per IP:

10.0.164.151                                             9
     /system/set.php                                     1
     /statistics/remove.php?name=jR-dngPNKv              1
     /printer/request.php?timeout=49188                  1
     /system/search.php                                  1
     /main/add.php?id=36010                              1
10.0.28.168                                              8
     /main/request.php                                   2
     /kernel/set.php?id=56568                            1
     /statistics/search.php                              1
     /kernel/remove.php?key=AhpyQ_ZXRF                   1
     /statistics/get.php?name=upDTNAXjId                 1
[ ... suppressed output ... ]
```

- Extract percentage of successful/unsuccessful requests
```
./http_log_parser.py  -f ../apache-httpd.log -s success,unsuccess

* Percentage of successful requests (anything 2xx or 3xx): 67.41%

* Percentage of unsuccessful requests (not 3xx or 3xx): 32.59%
```

- Get all possible statistics
```
./http_log_parser.py  -f ../apache-httpd.log

* The total number of requests made every minute:

31/Oct/1994:14:00     120
31/Oct/1994:14:01     124
[ ... suppressed output ... ]
31/Oct/1994:23:58     119
31/Oct/1994:23:59     115

* Top 10 requested pages (page - total requests):

/printer/remove.php                                 1627
/printer/search.php                                 1581
/printer/request.php                                1559
/system/add.php                                     1544
/main/add.php                                       1542
/main/list.php                                      1542
/system/call.php                                    1542
/finance/call.php                                   1538
/statistics/list.php                                1537
/kernel/set.php                                     1536

* Top 10 unsuccessful page requests (page - total requests):

/statistics/set.php                                 526
/main/request.php                                   524
/finance/remove.php                                 523
/system/get.php                                     516
/printer/search.php                                 513
/system/search.php                                  512
/kernel/set.php                                     511
/kernel/get.php                                     510
/printer/remove.php                                 506
/printer/call.php                                   506

* Top 10 IPs making the most requests (ip - total requests) with top 10 requested pages per IP:

10.0.164.151                                             9
     /printer/request.php                                1
     /finance/search.php                                 1
     /system/set.php                                     1
     /statistics/remove.php                              1
     /system/search.php                                  1
10.0.28.168                                              8
     /main/request.php                                   2
     /kernel/remove.php                                  1
     /statistics/search.php                              1
     /statistics/get.php                                 1
     /kernel/search.php                                  1
[ ... suppressed output ... ]

* Percentage of successful requests (anything 2xx or 3xx): 67.41%

* Percentage of unsuccessful requests (not 3xx or 3xx): 32.59%
```


## PERFORMANCE
Performance tested on MacBook Pro (Retina, 13-inch, Mid 2014) with
- 2.6 GHz Intel Core i5
- 8 GB 1600 MHz DDR3
- SSD hard drive

- ~10G test log file
```
time ./http_log_parser.py  -f ../apache-httpd-big.log 
[ ... suppressed output ... ]
real	11m57.418s
user	11m32.707s
sys	0m11.547s
```
- ~7M test log file (provided with current Code Challenge)
```
time ./http_log_parser.py  -f ../apache-httpd.log
[ ... suppressed output ... ]
real	0m0.852s
user	0m0.772s
sys	0m0.047s
```


## UNIT TESTS
The http_log_parser.py comes with unit tests, located in test_http_log_parser.py
Before executing unit tests please ensure that mytest (http_log_parser.py) has been installed. To install it run
```
pip install pytest
```

To run all tests type
```
./test_http_log_parser.py -v
=============================================================================== test session starts ===============================================================================
platform darwin -- Python 2.7.12, pytest-3.1.3, py-1.4.34, pluggy-0.4.0 -- /usr/local/opt/python/bin/python2.7
cachedir: .cache
rootdir: /Users/vklindukh/PycharmProjects/http_log_parser, inifile:
collected 6 items 

test_http_log_parser.py::test_parser_error PASSED
test_http_log_parser.py::test_parser_single_line PASSED
test_http_log_parser.py::test_parser_multiply_lines PASSED
test_http_log_parser.py::test_parser_nostrip_lines PASSED
test_http_log_parser.py::test_selective_parser PASSED
test_http_log_parser.py::test_standart_output_for_percentage PASSED

============================================================================ 6 passed in 0.01 seconds =============================================================================
```

## KNOW LIMITATIONS
- the regular expression is hardcoded into http_log_parser.py script. In order to support different formats you have to modify it (global variable REGEXP)
- script does not support mupltiply client IPs (separated by comma)
- the script is single-threaded. To increase performance you may want to refactor it in order to run several parsers in parallel (depends on number of CPU cores)

