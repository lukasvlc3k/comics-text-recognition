import os
import os.path
import cv2


# saves stats based on training dataset to csv file
# csv format:
# filename;bubble_id;area;area/full_page_area;perimeter;is_convex;x;y;w;h;w/full_page_w;h/full_page_h
def get_stats_on_training_dataset(labels_base_dir, csv_results_path):
    with os.scandir(labels_base_dir) as entries:
        with open(csv_results_path, "w") as f_stats:
            for entry in entries:
                name = entry.name

                print("Working on " + name)

                img = cv2.imread(entry.path, 0)
                ret, thresh = cv2.threshold(img, 127, 255, 0)
                contours, hierarchy = cv2.findContours(thresh, 1, 2)

                img_area = img.shape[0] * img.shape[1]

                contour_id = 0
                for contour in contours:
                    contour_id += 1
                    area = cv2.contourArea(contour)
                    area_ratio = area / img_area
                    perimeter = cv2.arcLength(contour, True)
                    convex = cv2.isContourConvex(contour)

                    if area < 75:
                        continue

                    x, y, w, h = cv2.boundingRect(contour)
                    w_ratio = w / img.shape[1]
                    h_ratio = h / img.shape[1]

                    line = name + ";" + str(contour_id) + ";" + str(area) + ";" + str(area_ratio) + ";" + \
                           str(perimeter) + ";" + str(convex) + ";" + str(x) + \
                           ";" + str(y) + ";" + str(w) + ";" + str(h) + ";" + str(w_ratio) + ";" + str(h_ratio)

                    f_stats.write(line + "\n")
