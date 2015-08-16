#!/usr/bin/python


# the cmd input arguments.
class arguments(object):
    def __init__(self):
        self.requests_count = 1
        self.concurrency = 1
        self.timelimit = 0
        self.timeout = 30
        self.windowsize = 0
        self.content_type = "text/plain"
        self.keep_alive = False
        self.print_version = False
        self.print_usage = False


class connection_times(object):
    __slots__ = ('start_time', 'wait_time', 'con_time', 'time')
    # start_time   time of starting the connection
    # wait_time     time of between request and response.
    # connect_time   time to connect
    # time           time for connection


def make_request_content(params):
    content = ""
    return content


# control the connectins
class connections(object):
    def __init__(self):
        pass

    def send_connection(self, content):
        return None

    def read_connection(self):
        return None

    def start_connnection(self):
        return connection
