from projector import Projector, gray_block
from process_proxy import make_proxy
import time

#print(gray_block(3).astype(int))
#exit(0)

for i in range(1):
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
    print("Monitor: " + str(p.get_monitor()))
    print("Waiting...")
    time.sleep(1)
    print("Cycling column gray codes...")
    for b in range(p.get_gray_bits_width()):
        p.show_gray_cols(b)
        time.sleep(0.2)
    print("Cycling row gray codes...")
    for b in range(p.get_gray_bits_height()):
        p.show_gray_rows(b)
        time.sleep(0.2)
    print("Stopping projector")
    p.stop()
    print("Projector stopped")
    print("Waiting")
    time.sleep(2)
    print("Done.")

print("All done; exiting")