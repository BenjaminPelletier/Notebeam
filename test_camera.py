import Image
import select
import v4l2capture  # sudo apt-get install libv4l-dev, sudo apt install v4l-utils

video = v4l2capture.Video_device("/dev/video0")
size_x, size_y = video.set_format(1920, 1080)
video.create_buffers(1)
video.queue_all_buffers()
video.start()

# Wait for the device to fill the buffer.
select.select((video,), (), ())

image_data = video.read()
video.close()
image = Image.frombytes("RGB", (size_x, size_y), image_data)
image.save("image.jpg")
print "Saved image.jpg (Size: " + str(size_x) + " x " + str(size_y) + ")"
