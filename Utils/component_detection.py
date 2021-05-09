import cv2


def get_components(image):
    connectivity = 4  # number of directions (neighbors finding)
    output = cv2.connectedComponentsWithStats(image, connectivity, cv2.CV_32S)

    num_labels = output[0]
    labels = output[1]
    stats = output[2]
    centroids = output[3]

    return num_labels, labels, stats, centroids
