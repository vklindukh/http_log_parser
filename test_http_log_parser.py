#!/usr/bin/env py.test

from http_log_parser import STATS_FULL_LIST, Parser

test_data = \
"""10.0.176.70 - - [31/Oct/1994:14:00:57 +0000] "POST /kernel/get.php?aws=nLZQtFvpe HTTP/1.0" 403 1162
10.0.139.231 - - [31/Oct/1994:14:00:57 +0000] "GET /kernel/get.php? HTTP/1.0" 404 704
10.0.176.70 - - [31/Oct/1994:14:00:58 +0000] "GET /printer/remove.php HTTP/1.0" 200 32980
10.0.139.231 - - [31/Oct/1994:14:00:58 +0000] "GET /main/set.php?timeout=37340 HTTP/1.1" 404 921
10.0.176.70 - - [31/Oct/1994:14:00:59 +0000] "GET /statistics/call.php?secret=yIKdbrpuPn HTTP/1.0" 404 931
10.0.139.231 - - [31/Oct/1994:14:00:59 +0000] "POST /finance/add.php HTTP/1.1" 300 1521
10.0.138.11 - - [31/Oct/1994:14:00:59 +0000] "GET /printer/add.php?id=40762 HTTP/1.1" 200 46883
10.0.176.70 - - [31/Oct/1994:14:01:00 +0000] "POST /kernel/search.php HTTP/1.0" 200 45161
10.0.139.231 - - [31/Oct/1994:14:01:00 +0000] "POST /kernel/remove.php?value=47092 HTTP/1.1" 200 330
10.0.138.11 - - [31/Oct/1994:14:01:00 +0000] "GET /main/call.php HTTP/1.0" 204 32812
10.0.173.104 - - [31/Oct/1994:14:01:00 +0000] "POST /statistics/get.php?session=WEriQXgwqI HTTP/1.0" 204 53749
10.0.173.104 - - [31/Oct/1994:14:01:01 +0000] "POST /kernel/remove.php?session=B_rJQysxFn HTTP/1.1" 204 34156
10.0.133.214 - - [31/Oct/1994:14:01:02 +0000] "GET /main/add.php?age=34664 HTTP/1.0" 200 45132
10.0.139.231 - - [31/Oct/1994:14:01:03 +0000] "POST /statistics/get.php?aws=LTkzQjctib HTTP/1.0" 204 1776
10.0.176.70 - - [31/Oct/1994:14:01:03 +0000] "POST /main/search.php HTTP/1.1" 200 1349
10.0.139.231 - - [31/Oct/1994:14:01:04 +0000] "POST /kernel/remove.php?age=58234 HTTP/1.0" 200 1997
10.0.133.214 - - [31/Oct/1994:14:01:04 +0000] "GET /kernel/search.php?age=49039 HTTP/1.0" 204 33997
10.0.139.231 - - [31/Oct/1994:14:01:05 +0000] "GET /kernel/get.php?timeout=42514 HTTP/1.0" 304 1285
"""

def test_parser_error():
    parser = Parser(dict(map(lambda x: [x, True], STATS_FULL_LIST.split(","))), True)
    parser.process('unparsed string')

    assert (parser.counter['total'] == 0)

def test_parser_single_line():
    parser = Parser(dict(map(lambda x: [x, True], STATS_FULL_LIST.split(","))), True)
    parser.process(test_data.splitlines()[0])

    assert (parser.counter['total'] == 1)
    assert (parser.counter['success'] == 0)
    assert (parser.counter['unsuccess'] == 1)
    assert (parser.counter['url'] == {'/kernel/get.php': 1})
    assert (parser.counter['urlunsuccess'] == {'/kernel/get.php': 1})
    assert (parser.counter['ips'] == {'10.0.176.70': 1})
    assert (parser.counter['ippages'] == {'10.0.176.70': {'/kernel/get.php': 1}})
    assert (parser.counter['timestat'] == {'31/Oct/1994:14:00': 1})

def test_parser_multiply_lines():
    parser = Parser(dict(map(lambda x: [x, True], STATS_FULL_LIST.split(","))), True)
    global test_data
    for l in test_data.splitlines():
        parser.process(l)

    assert (parser.counter['total'] == 18)
    assert (parser.counter['success'] == 14)
    assert (parser.counter['unsuccess'] == 4)
    assert (parser.counter['url'] == {'/printer/add.php': 1,
                                      '/main/set.php': 1,
                                      '/main/add.php': 1,
                                      '/main/call.php': 1,
                                      '/main/search.php': 1,
                                      '/statistics/call.php': 1,
                                      '/statistics/get.php': 2,
                                      '/finance/add.php': 1,
                                      '/kernel/get.php': 3,
                                      '/kernel/search.php': 2,
                                      '/kernel/remove.php': 3,
                                      '/printer/remove.php': 1
                                      })
    assert (parser.counter['urlunsuccess'] == {'/kernel/get.php': 2,
                                               '/main/set.php': 1,
                                               '/statistics/call.php': 1
                                               })
    assert (parser.counter['ips'] == {'10.0.133.214': 2,
                                      '10.0.138.11': 2,
                                      '10.0.173.104': 2,
                                      '10.0.139.231': 7,
                                      '10.0.176.70': 5})
    assert (parser.counter['ippages'] == {'10.0.133.214': {'/main/add.php': 1, '/kernel/search.php': 1},
                                          '10.0.138.11': {'/printer/add.php': 1, '/main/call.php': 1},
                                          '10.0.173.104': {'/statistics/get.php': 1, '/kernel/remove.php': 1},
                                          '10.0.139.231': {'/kernel/get.php': 2, '/main/set.php': 1,
                                                           '/finance/add.php': 1, '/kernel/remove.php': 2,
                                                           '/statistics/get.php': 1},
                                          '10.0.176.70': {'/kernel/get.php': 1, '/printer/remove.php': 1,
                                                          '/statistics/call.php': 1, '/kernel/search.php': 1,
                                                          '/main/search.php': 1}})
    assert (parser.counter['timestat'] == {'31/Oct/1994:14:00': 7, '31/Oct/1994:14:01': 11})

def test_parser_nostrip_lines():
    parser = Parser(dict(map(lambda x: [x, True], STATS_FULL_LIST.split(","))), False)
    global test_data
    for l in test_data.splitlines()[:3]:
        parser.process(l)

    assert (parser.counter['total'] == 3)
    assert (parser.counter['success'] == 1)
    assert (parser.counter['unsuccess'] == 2)
    assert (parser.counter['url'] == {'/kernel/get.php?aws=nLZQtFvpe': 1,
                                      '/kernel/get.php?': 1,
                                      '/printer/remove.php': 1})
    assert (parser.counter['urlunsuccess'] == {'/kernel/get.php?aws=nLZQtFvpe': 1,
                                               '/kernel/get.php?': 1})
    assert (parser.counter['ips'] == {'10.0.139.231': 1,
                                      '10.0.176.70': 2})
    assert (parser.counter['ippages'] == {'10.0.139.231': {'/kernel/get.php?': 1},
                                          '10.0.176.70': {'/kernel/get.php?aws=nLZQtFvpe': 1,
                                                          '/printer/remove.php': 1}})
    assert (parser.counter['timestat'] == {'31/Oct/1994:14:00': 3})

def test_selective_parser():
    parser = Parser(dict(map(lambda x: [x, True], "top10,success,unsuccess".split(","))), True)
    global test_data
    for l in test_data.splitlines()[:3]:
        parser.process(l)

    assert (parser.counter['total'] == 3)
    assert (parser.counter['success'] == 1)
    assert (parser.counter['unsuccess'] == 2)
    assert (parser.counter['url'] == {'/kernel/get.php': 2,
                                      '/printer/remove.php': 1})
    assert (parser.counter['urlunsuccess'] == dict())
    assert (parser.counter['ips'] == dict())
    assert (parser.counter['ippages'] == dict())
    assert (parser.counter['timestat'] == dict())


def test_standart_output_for_percentage(capsys):
    parser = Parser(dict(map(lambda x: [x, True], "success,unsuccess".split(","))), True)
    global test_data
    for l in test_data.splitlines():
        parser.process(l)
    parser.print_stat()
    out, err = capsys.readouterr()
    expected_out = \
"""
* Percentage of successful requests (anything 2xx or 3xx): 77.78%

* Percentage of unsuccessful requests (not 3xx or 3xx): 22.22%
"""
    assert (out == expected_out)