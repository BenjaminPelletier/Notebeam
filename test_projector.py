from projector import Projector
from process_proxy import make_proxy
import time

for i in range(2):
    print("Instantiating projector")
    projector = Projector()
    print("Making proxy")
    p = make_proxy(projector)
    print("Deleting original projector")
    del projector
    print("Displaying projector")
    p.show()
    print("Projector displayed")
    print("Getting monitor")
    print("Monitor: " + str(p.getMonitor()))
    print("Waiting...")
    time.sleep(2)
    print("Stopping projector")
    p.stop()
    print("Projector stopped")
    print("Waiting")
    time.sleep(2)
    print("Done.")

print("All done; exiting")