#!/usr/bin/env python
#
# Usage: To get command-line options run http_log_parser.py -h
#

import argparse
import re

# list of statistics calculated and displayed by default.
STATS_FULL_LIST = "top10,success,unsuccess,top10unsuccess,top10ips,timestat"

# regex which extracts 4 fields from string:
#   - client IP (named group IP)
#   - date (named group DATE)
#   - url (with args) (named group URK)
#   - HTTP response code (named group CODE)
# below is example of line which match regular expression
# 10.0.79.88 - - [31/Oct/1994:23:51:30 +0000] "GET /system/set.php?secret=-JjAftwIBD HTTP/1.0" 204 37221
#
# you may want to update regex in case of different log format. keep the group naming for full compatibility
REGEXP = "^(?P<IP>[0-9.]+)\s+-\s+-\s+\[(?P<DATE>\S+)\s+\S+\]\s+\"\S+\s+(?P<URL>\S+)\s+\S+\"\s+(?P<CODE>\d+)\s+\d+$"

#
# parse command-line options
#
class Options(object):
    def __init__(self):
        global STATS_FULL_LIST
        parser = argparse.ArgumentParser()
        parser.add_argument("-f", "--file", dest="file",
                            help="apache access log to process")
        parser.add_argument("-s", "--statistics", dest="statistics", default=STATS_FULL_LIST,
                            help="list of coma separated statistics to be calculated. Default is %s" % STATS_FULL_LIST)
        parser.add_argument("-q", action="store_false", dest="strip", default=True,
                            help="include query string into URL. Strip by default")

        self.args = parser.parse_args()

        if not self.args.file:
            parser.error("file name is required")

        self.slist = dict(map(lambda x: [x, True], self.args.statistics.split(",")))

    #
    # method returns dictionary, where the key is name of statistic requested
    # and the value is True
    # see STATS_FULL_LIST for full list of supported statistics
    #
    def get_stat_list(self):
        return self.slist

    def get_filename(self):
        return self.args.file

    def strip_query_string(self):
        return self.args.strip


#
# apache-log parser. extracts metrics from log file, calculates statistics, display results
#
class Parser(object):
    def __init__(self, slist, strip):
        global REGEXP
        self.strip = strip
        # slist varable contains list of statistics requested
        self.slist = slist
        # counters, one per each statistic requested
        self.counter = dict()
        self.counter['total'] = 0
        self.counter['success'] = 0
        self.counter['unsuccess'] = 0
        self.counter['url'] = dict()
        self.counter['urlunsuccess'] = dict()
        self.counter['ips'] = dict()
        self.counter['ippages'] = dict()
        self.counter['timestat'] = dict()
        # extract 4 fields from string:
        #   - client IP
        #   - date
        #   - url (with args)
        #   - HTTP response code
        # example of correctly parsed string:
        # 10.0.79.88 - - [31/Oct/1994:23:51:30 +0000] "GET /system/set.php?secret=-JjAftwIBD HTTP/1.0" 204 37221
        self.matcher = re.compile(REGEXP)

    #
    # parser method. process single line, extract metrics and calculates statistics requested
    #
    def process(self, l):
        g = self.matcher.match(l.strip())
        if g is None:
            print "unable to parse string {}".format(l)
            return

        url = g.group(3)
        if self.strip:
            url = url.split("?")[0]
        data_strip = g.group(2)[:-3]

        self.counter['total'] += 1

        if 'top10ips' in self.slist:
            self.process_list('ips', g.group(1))
            self.process_dict('ippages', g.group(1), url)

        if 'top10' in self.slist:
            self.process_list('url', url)

        if 'top10unsuccess' in self.slist:
            self.process_list_unsuccess(url, g.group(4))

        if 'success' in self.slist or 'unsuccess' in self.slist:
            self.process_total(g.group(4))

        if 'timestat' in self.slist:
            self.process_list('timestat', data_strip)

    #
    # internal method. It gets param/key pair and updates the nested dictionary:
    #   - creates new element, if not exist
    #   - increases counter
    #
    def process_list(self, param, key):
        if key not in self.counter[param]:
            self.counter[param][key] = 1
        else:
            self.counter[param][key] += 1

    #
    # internal method. It gets param and key/value pair and updates the nested dictionaries:
    #   - creates new element (empty nested dictionary) if not exist
    #   - inside nested dictionary:
    #      - creates new element, if not exist
    #      - increases counter
    #
    def process_dict(self, param, key, key2):
        if key not in self.counter[param]:
            self.counter[param][key] = dict()

        if key2 not in self.counter[param][key]:
            self.counter[param][key][key2] = 1
        else:
            self.counter[param][key][key2] += 1

    #
    # internal method. calls self.process_list() (i.e. updates counters) only for unsuccessful requests
    #
    def process_list_unsuccess(self, url, code):
        if not self.success(code):
            self.process_list('urlunsuccess', url)

    #
    # internal method. updated 'success' on 'unsuccess' counters depending on HTTP response code
    #
    def process_total(self, code):
        if self.success(code):
            self.counter['success'] += 1
        else:
            self.counter['unsuccess'] += 1

    #
    # internal method. Check HTTP response code and returns 'True' forr successful and 'Flase' for unsuccessful requests
    #
    def success(self, code):
        if code.startswith('2') or code.startswith('3'):
            return True
        else:
            return False

    #
    # print requested statistics to STDOUT
    #
    def print_stat(self):

        if 'timestat' in self.slist:
            print "\n* The total number of requests made every minute:\n"
            for k, v in sorted(self.counter['timestat'].items(), key=lambda x: x[0], reverse=False):
                print "{:<20}  {}".format(k, v)

        if 'top10' in self.slist:
            print "\n* Top 10 requested pages (page - total requests):\n"
            for k, v in sorted(self.counter['url'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print "{:<50}  {}".format(k, v)

        if 'top10unsuccess' in self.slist:
            print "\n* Top 10 unsuccessful page requests (page - total requests):\n"
            for k, v in sorted(self.counter['urlunsuccess'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print "{:<50}  {}".format(k, v)

        if 'top10ips' in self.slist:
            print "\n* Top 10 IPs making the most requests (ip - total requests) with top 10 requested pages per IP:\n"
            for k, v in sorted(self.counter['ips'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print "{:<55}  {}".format(k, v)
                for i, j in sorted(self.counter['ippages'][k].items(), key=lambda x: x[1], reverse=True)[:10]:
                    print "     {:<50}  {}".format(i, j)

        if 'success' in self.slist:
            print "\n* Percentage of successful requests (anything 2xx or 3xx): {:3.2f}%". \
                format(float(self.counter['success']) / float(self.counter['total']) * 100)

        if 'unsuccess' in self.slist:
            print "\n* Percentage of unsuccessful requests (not 3xx or 3xx): {:3.2f}%". \
                format(float(self.counter['unsuccess']) / float(self.counter['total']) * 100)


def main():
    options = Options()

    parser = Parser(options.get_stat_list(), options.strip_query_string())
    with open(options.get_filename()) as f:
        for l in f:
            parser.process(l)
    f.close()

    parser.print_stat()


if __name__ == '__main__':
    main()
