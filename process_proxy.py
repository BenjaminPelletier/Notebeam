import os, errno
import pickle, struct


CODE_OK = 'ok'
CODE_EXCEPTION = 'error'


class ProcessProxy:
    def __init__(self, req_w, resp_r):
        self.req_w = req_w
        self.resp_r = resp_r

    def request(self, method_name, args):
        send_outgoing(self.req_w, (method_name, args), "parent")
        code, response = read_incoming(self.resp_r, "parent")
        #print("Parent received code %s response %s" % (code, str(response)))

        if code == CODE_OK:
            return response
        elif code == CODE_EXCEPTION:
            raise response
        else:
            raise ValueError('Remote proxy server returned an invalid result code: %s' % str(code))

    def __del__(self):
        #print("Parent deleting")
        self.req_w.close()
        self.resp_r.close()
        #print("Parent deleted")


def serve_from_child(child_class, req_r, resp_w):
    #print("serve_from_child")
    while True:
        cmd = read_incoming(req_r, "child")
        #print("Child command received: " + str(cmd))
        if cmd is None:
            break
        try:
            method_name, args = cmd
            method = getattr(child_class, method_name)
            result = (CODE_OK, method(*args))
        except Exception as e:
            result = (CODE_EXCEPTION, e)
        #print("Child result " + str(result))
        try:
            send_outgoing(resp_w, result, "child")
            #print("Child sent Ok")
        except IOError as e:
            if e.errno == errno.EPIPE:
                break
            print("Child send error: " + str(e))
            break
    #print("Child exited loop")


def make_proxy(remote_class):
    req_r, req_w = os.pipe()
    req_r, req_w = os.fdopen(req_r, 'r', 0), os.fdopen(req_w, 'w', 0)
    resp_r, resp_w = os.pipe()
    resp_r, resp_w = os.fdopen(resp_r, 'r', 0), os.fdopen(resp_w, 'w', 0)

    pid = os.fork()
    if pid:  # Parent
        req_r.close()
        resp_w.close()

        client = ProcessProxy(req_w, resp_r)

        def build_request(client, method_name):
            return (lambda self, *args: client.request(method_name, args)).__get__(client)

        for method_name in dir(remote_class):
            if method_name.startswith('__'):
                continue
            method = getattr(remote_class, method_name)
            if not callable(method):
                continue
            #print("%s is a valid method" % method_name)
            setattr(client, method_name, build_request(client, method_name))

        return client

    else:  # Child
        req_w.close()
        resp_r.close()

        serve_from_child(remote_class, req_r, resp_w)

        #print("Child process exiting")
        exit(0)


def read_incoming(r, who):
    #print("%s reading 4 byte length" % who)
    plen = bytearray(r.read(4))
    #print("%s read %i length bytes" % (who, len(plen)))
    if len(plen) < 4:
        return None
    plen = bytearray_to_int(plen)
    #print("%s reading %d bytes" % (who, plen))
    payload = r.read(plen)
    #print("%s received %i bytes" % (who, len(payload)))
    if len(payload) == 0:
        return None
    if len(payload) < plen:
        print("Whoops; need to put payload read in loop")
        return None
    return pickle.loads(payload)


def send_outgoing(w, obj, who):
    #print(("%s sending object " % who) + str(obj))
    payload = bytearray(pickle.dumps(obj))
    #print("%s writing length code" % who)
    w.write(int_to_bytearray(len(payload)))
    #print("%s writing %d bytes" % (who, len(payload)))
    w.write(payload)
    #print("%s flushing" % who)
    w.flush()


def int_to_bytearray(v):
    return struct.pack("<L", v)


def bytearray_to_int(b):
    return struct.unpack("<L", b)[0]
