from optparse import OptionParser
import re

STATS_FULL_LIST = "top10,success,unsuccess,top10unsuccess,top10ips,timestat"


class Options(object):
    def __init__(self, stats_list):
        self.stats_list = stats_list

        parser = OptionParser()
        parser.add_option("-f", "--file", dest="file",
                          help="apache access log to process")
        parser.add_option("-s", "--statistics", dest="statistics", default=self.stats_list,
                          help="list of coma separated statistics to be calculated. Default is %s" % self.stats_list)
        parser.add_option("-q", action="store_false", dest="strip", default=True,
                          help="include query string into URL. Strip by default")

        (self.options, args) = parser.parse_args()
        if not self.options.file:
            parser.error("file name is required")

    def get_stat_list(self):
        slist = dict(map(lambda x: [x, False], self.stats_list.split(",")))
        for s in self.options.statistics.split(","):
            slist[s] = True
        return slist

    def get_filename(self):
        return self.options.file

    def strip_query_string(self):
        return self.options.strip


class Parser(object):
    def __init__(self, stats_list, strip):
        self.strip = strip
        self.stats_list = stats_list
        self.counter = dict()
        self.counter['total'] = 0
        self.counter['success'] = 0
        self.counter['unsuccess'] = 0
        self.counter['url'] = dict()
        self.counter['urlunsuccess'] = dict()
        self.counter['ips'] = dict()
        self.counter['ippages'] = dict()
        self.counter['timestat'] = dict()

        self.matcher = re.compile(r"^([0-9.]+)\s+-\s+-\s+\[(\S+)\s+\S+\]\s+\"\S+\s+(\S+)\s+\S+\"\s+(\d+)\s+\d+$")

    def process(self, l):
        g = self.matcher.match(l.strip())
        url = g.group(3)
        if self.strip:
            url = url.split("?")[0]
        data_strip = g.group(2)[:-3]

        self.counter['total'] += 1

        if self.stats_list['top10ips']:
            self.process_list('ips', g.group(1))
            self.process_dict('ippages', g.group(1), url)

        if self.stats_list['top10']:
            self.process_list('url', url)

        if self.stats_list['unsuccess']:
            self.process_list_unsuccess(url, g.group(4))

        if self.stats_list['success'] or self.stats_list['unsuccess']:
            self.process_total(g.group(4))

        if self.stats_list['timestat']:
            self.process_list('timestat', data_strip)

    def process_list(self, param, value):
        if value not in self.counter[param]:
            self.counter[param][value] = 1
        else:
            self.counter[param][value] += 1

    def process_dict(self, param, value, value2):
        if value not in self.counter[param]:
            self.counter[param][value] = dict()

        if value2 not in self.counter[param][value]:
            self.counter[param][value][value2] = 1
        else:
            self.counter[param][value][value2] += 1

    def process_list_unsuccess(self, url, code):
        if not self.success(code):
            self.process_list('urlunsuccess', url)

    def process_total(self, code):
        if self.success(code):
            self.counter['success'] += 1
        else:
            self.counter['unsuccess'] += 1

    def success(self, code):
        if code.startswith('2') or code.startswith('3'):
            return True
        else:
            return False

    def print_stat(self):

        if self.stats_list['timestat']:
            print "\n* The total number of requests made every minute:\n"
            for k, v in sorted(self.counter['timestat'].items(), key=lambda x: x[0], reverse=False):
                print "{:<20}  {}".format(k, v)

        if self.stats_list['top10']:
            print "\n* Top 10 requested pages (page - total requests):\n"
            for k, v in sorted(self.counter['url'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print "{:<50}  {}".format(k, v)

        if self.stats_list['top10unsuccess']:
            print "\n* Top 10 unsuccessful page requests (page - total requests):\n"
            for k, v in sorted(self.counter['urlunsuccess'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print "{:<50}  {}".format(k, v)

        if self.stats_list['top10ips']:
            print "\n* Top 10 IPs making the most requests (ip - total requests) with top 10 requested pages per IP:\n"
            for k, v in sorted(self.counter['ips'].items(), key=lambda x: x[1], reverse=True)[:10]:
                print "{:<55}  {}".format(k, v)
                for i, j in sorted(self.counter['ippages'][k].items(), key=lambda x: x[1], reverse=True)[:10]:
                    print "     {:<50}  {}".format(i, j)

        if self.stats_list['success']:
            print "\n* Percentage of successful requests (anything 2xx or 3xx): {:3.2f}%". \
                format(float(self.counter['success']) / float(self.counter['total']) * 100)

        if self.stats_list['unsuccess']:
            print "\n* Percentage of unsuccessful requests (not 3xx or 3xx): {:3.2f}%". \
                format(float(self.counter['unsuccess']) / float(self.counter['total']) * 100)


def main():
    global STATS_FULL_LIST
    options = Options(STATS_FULL_LIST)

    parser = Parser(options.get_stat_list(), options.strip_query_string())
    with open(options.get_filename()) as f:
        for l in f:
            parser.process(l)
    f.close()

    parser.print_stat()


if __name__ == '__main__':
    main()
