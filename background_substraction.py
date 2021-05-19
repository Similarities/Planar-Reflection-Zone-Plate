import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import math
import os


# make sure the image-array (picture, background) is in 32bit
# chose either to substract a background image or roi in same image
# define two ROIS for RZP or one
class ImagePreProcessing:

    def __init__(self, picture, picture_name, background_name, roi_list):
        self.filename = picture_name
        self.picture = picture
        self.background = np.empty([])
        self.background_name = background_name
        # x1, y1, x2, y2
        self.back_roi = np.empty([])
        self.binned_roi_y = np.empty([])
        self.x_axis_eV = np.empty([])
        self.x_axis_nm = np.empty([])
        self.roi_list = roi_list

    def load_background_image_and_roi(self, image_array, roi, name):
        self.back_roi = roi
        self.background = image_array
        self.background_name = name
        return self.back_roi, self.background_name, self.background

    def reference_scaling_for_background_image(self, image_array, roi, name):
        self.load_background_image_and_roi(image_array, roi, name)
        # opens tif is flipped vertical, array_image[y:y1, x:x1] (warum auch immer....)
        subarray_reference = self.background[self.back_roi[1]:self.back_roi[3], self.back_roi[0]:self.back_roi[2]]
        subarray_picture = self.picture[self.back_roi[1]:self.back_roi[3], self.back_roi[0]:self.back_roi[2]]
        mean_background_reference_x = np.mean(subarray_reference, axis=0)
        mean_background_picture_x = np.mean(subarray_picture, axis=0)
        scaling_factor = np.mean(mean_background_picture_x / mean_background_reference_x)
        print("scalingfactor", scaling_factor)
        self.background[::] = self.background[::] * scaling_factor
        return self.background

    def background_from_same_picture(self, roilist_back):
        self.back_roi = roilist_back
        line_out_back_ground = np.sum(self.picture[self.back_roi[1]: self.back_roi[3], self.back_roi[0]: self.back_roi[2]], axis=0)
        line_out_per_row = line_out_back_ground[:] / (self.back_roi[3]-self.back_roi[1])
        x_axis = np.arange(0, self.back_roi[2]-self.back_roi[0])

        plt.figure(101)
        plt.plot(x_axis, line_out_per_row)

        plt.figure(1)
        plt.imshow(self.picture)

    def background_subtraction(self):
        for counter, x in enumerate(self.picture[0, ::]):
            self.picture[::, counter] = self.picture[::, counter] - self.background[::, counter]
        self.picture[self.picture < 0] = 0
        return self.picture

    def bin_in_y(self):
        self.binned_roi_y = np.sum(self.picture[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]],
                                   axis=0)
        self.x_axis_nm = np.arange(0, self.roi_list[2] - self.roi_list[0]).astype(np.float32)
        plt.figure(3)
        plt.imshow(self.picture[self.roi_list[1]:self.roi_list[-1], self.roi_list[0]: self.roi_list[2]])
        plt.colorbar()
        return self.binned_roi_y, self.x_axis_nm

    def scale_array_per_second(self, constant):
        self.binned_roi_y = basic_file_app.constant_array_scaling(self.binned_roi_y, constant)
        return self.binned_roi_y

    def save_sum_of_y(self):
        result = np.stack((self.x_axis_nm, self.binned_roi_y), axis=1)

        np.savetxt(self.filename[:-4] + '_binned_y' + ".txt", result, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')

    def view_control(self):
        plt.figure(1)
        plt.imshow(self.picture)
        plt.hlines(self.back_roi[1], xmax=2048, xmin=0)
        plt.hlines(self.back_roi[-1], xmax=2048, xmin=0)
        plt.vlines(self.back_roi[0], ymax=2048, ymin=0)
        plt.vlines(self.back_roi[2], ymax=2048, ymin=0)

    def figure_raw(self):
        plt.figure(8)
        plt.imshow(self.picture)
        plt.colorbar()


path = "data/20210312/210312/45ms_center/210312_PM015844.tif"
picture = basic_image_app.read_image(path)
# sometimes python opens pictures differently then other editors (imageJ e.g.)
picture = np.flip(picture, axis = 0)
roi_list = ([750,516, 2048, 789])
roi_list_back = ([750, 798, 2048, 951])
Test = ImagePreProcessing(picture, "test", "on picture roi", roi_list)
Test.background_from_same_picture(roi_list_back)

plt.show()
