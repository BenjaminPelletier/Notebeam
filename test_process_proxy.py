from process_proxy import make_proxy
import time


class Asdf:
    def do_thing(self, delay, msg):
        print("Asdf.do_thing %i %s" % (delay, msg))
        time.sleep(delay)
        print("Asdf.do_thing %i %s complete" % (delay, msg))

    def throw_exception(self, msg):
        raise ValueError(msg)


asdf = Asdf()
print("Making proxy")
proxy = make_proxy(asdf)
print("Proxy made")

print("proxy.do_thing")
proxy.do_thing(2, "qwerty")
print("proxy.throw_exception")
try:
    proxy.throw_exception("hello")
    print("Exception NOT caught!")
except Exception as e:
    print("Caught %s: %s" % (str(type(e)), e.message))
print("Deleting client")
del proxy
print("Complete")