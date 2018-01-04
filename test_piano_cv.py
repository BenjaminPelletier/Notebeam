import numpy as np
import cv2
from scipy import ndimage
import matplotlib.pyplot as plt

def show_labels(labels):
    label_hue = np.uint8(179 * labels / np.max(labels))
    blank_ch = 255 * np.ones_like(label_hue)
    labeled_img = cv2.merge([label_hue, blank_ch, blank_ch])
    labeled_img = cv2.cvtColor(labeled_img, cv2.COLOR_HSV2BGR)
    labeled_img[labels == 0] = 0
    return labeled_img


def reduce_hull(hull, n):
    shape = list(reversed(np.ravel(np.max(hull, 0) + 2)))
    mask0 = np.zeros(shape)
    cv2.fillConvexPoly(mask0, hull, 255)

    while hull.shape[0] > n:
        i_best = None
        n_best = shape[0] * shape[1] + 1
        for i in range(hull.shape[0]):
            mask1 = np.zeros(shape)
            subhull = np.delete(np.copy(hull), i, axis=0)
            cv2.fillConvexPoly(mask1, subhull, 255)

            mask1 = np.logical_xor(mask0, mask1)
            n_changed = np.sum(mask1)
            if n_changed < n_best:
                i_best = i
                n_best = n_changed

        hull = np.delete(hull, i_best, axis=0)

    return hull


def project_line(z, p0, p1, n):
    y0 = p0[0]
    x0 = p0[1]
    y1 = p1[0]
    x1 = p1[1]
    x, y = np.linspace(x0, x1, n), np.linspace(y0, y1, n)
    return ndimage.map_coordinates(z, np.vstack((x, y)), order=1)


fnames = ['piano1.jpg', 'piano2.jpg', 'piano3.jpg', 'piano4.jpg']
for fname in fnames:
    print(fname)

    # Read image
    fd = open(fname)
    img_str = fd.read()
    fd.close()
    nparr = np.fromstring(img_str, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

    # Look for bright areas in the image
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, th1 = cv2.threshold(gray, 127, 255, cv2.THRESH_BINARY)

    kernel = np.ones((5, 5), np.uint8)
    kernel[0,0] = 0
    kernel[4,0] = 0
    kernel[0,4] = 0
    kernel[4,4] = 0
    th1 = cv2.morphologyEx(th1, cv2.MORPH_CLOSE, kernel)

    # Pick out the largest reasonable candidate blob as the keyboard
    _, markers = cv2.connectedComponents(th1)

    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(th1, 8, cv2.CV_32S)

    candidate_indices = []
    for i in range(1, num_labels):
        s = tuple(stats[i])
        ff = float(s[4]) / np.prod(gray.shape)

        if ff < 0.01:
            continue
        if ff > 0.5:
            continue

        candidate_indices.append(i)

    if len(candidate_indices) != 1:
        print("%i candidates for keyboard" % len(candidate_indices))
        exit(0)

    # Mask for the keyboard's convex hull
    mask = (labels == candidate_indices[0]).astype(np.uint8)
    _, contours, hierarchy = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    rect = cv2.minAreaRect(contours[0])
    hull = cv2.convexHull(contours[0])

    mask = np.zeros(mask.shape)
    cv2.fillConvexPoly(mask, hull, 255)

    # Re-threshold the image with a better thresholding operation
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    ret3, th3 = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    th3[mask == 0] = 0

    # Find the bounding quadrilateral around the keyboard
    kb_quad = np.squeeze(reduce_hull(hull, 4))

    # Make sure points are listed clockwise
    winding = kb_quad[0,0]*kb_quad[1,1] - kb_quad[0,1]*kb_quad[1,0]
    if winding < 0:
        kb_quad = np.flipud(kb_quad)

    # Make sure longest side is p0-p1
    p0 = kb_quad
    p1 = kb_quad[[1,2,3,0], :]
    dp = np.sqrt(np.sum(np.power(p1 - p0, 2), axis=1))
    i_max = np.argmax(dp)
    kb_quad = kb_quad[np.mod(np.array([0,1,2,3]) + i_max, 4), :]

    # Extract key brightnesses
    pixel_subsampling = 10
    n = int(pixel_subsampling*dp[i_max])
    kb0 = project_line(gray, 0.75*kb_quad[0,:]+0.25*kb_quad[3,:], 0.75*kb_quad[1,:]+0.25*kb_quad[2,:], n)
    kb1 = project_line(gray, 0.25*kb_quad[0,:]+0.75*kb_quad[3,:], 0.25*kb_quad[1,:]+0.75*kb_quad[2,:], n)

    # Make sure kb0 is the chromatic side of the keyboard
    if np.std(kb0) < np.std(kb1):
        temp = kb0
        kb0 = kb1
        kb1 = temp
        kb_quad = kb_quad[[2, 3, 0, 1], :]

    # Estimate key spacing via autocorrelation
    min_key_width = 3 # pixels
    max_key_width = img.shape[1] / 30 # pixels

    kb1f = kb1.astype(float)
    kb1f = kb1f - np.mean(kb1f)
    sigma2 = np.power(np.std(kb1f), 2)
    i0 = min_key_width * pixel_subsampling
    i1 = max_key_width * pixel_subsampling
    n = len(kb1) - i1
    ac = np.zeros([i1-i0+1], float)
    for i in range(0, i1-i0+1):
        ac[i] = np.mean(kb1f[0:n] * kb1f[i:n+i]) / sigma2
    period = np.argmax(ac[i0:]) + i0

    # Estimate key spacing offset
    ac = np.zeros([period], float)
    for i in range(len(kb1f)):
        ac[i % period] += kb1f[i]
    phase = np.argmin(ac)

    # Refine key spacing
    def score(phase, period0, dPeriod):
        x = np.arange(0, len(kb1f), dtype=float)
        weight = np.zeros_like(x)
        c = phase
        while c <

    plt.plot(kb1f)
    for i in range(phase, len(kb1f), period):
        plt.plot([i, i], [min(kb1f), max(kb1f)])
    plt.show()



    for i in range(4):
        cv2.putText(img, 'p' + str(i), tuple(np.ravel(kb_quad[i,:])), cv2.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 2, cv2.LINE_AA)

    #rect = cv2.minAreaRect(contours[0])
    #box = cv2.boxPoints(rect)
    #print(rect)

    #cv2.drawContours(img, [hull], 0, (0, 0, 255), 2)

    #thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 21, 2)

    #cv2.imshow('piano', show_labels(labels))
    cv2.imshow('piano', img)
    cv2.waitKey(0)
