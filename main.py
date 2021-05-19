import matplotlib.pyplot as plt
import numpy as np
import basic_image_app
import basic_file_app
import math
import plot_filter
import px_shift_on_picture_array
import calibration_analytical_from_array
import os

class PxCorrectionOnStack:
    def __init__(self, path, reference_point_list):
        self.path = path
        self.file_list = basic_image_app.get_file_list(path_picture)
        self.reference_points = reference_point_list
        self.pre_process_stack()

    def pre_process_stack(self):
        for x in self.file_list:
            open_picture = basic_image_app.SingleImageOpen(x, path_picture)
            my_picture = open_picture.return_single_image()
            PreProcess = ImagePreProcessing(my_picture, x, my_background, name_background[:-4], roi_list)
            # Test.view_control()
            PreProcess.reference_scaling()
            PreProcess.background_subtraction()
            PreProcess.bin_in_y()
            PreProcess.scale_array_per_second(per_second_correction)
            PreProcess.save_sum_of_y()
        print("xxxxxxxxx - all px shifted xxxxxxxxxxxx")

    def px_shift(self, path):
        self.file_list = basic_file_app.get_file_list(path)
        print(len(self.file_list))
        reference = basic_file_app.load_2d_array(self.file_list[0], 0, 1, 1)
        print("new file list", self.file_list)
        for x in self.file_list[1:]:
            image_array = basic_file_app.load_2d_array(x, 0, 1, 1)
            ShiftIt = px_shift_on_picture_array.PixelShift(reference, self.reference_points)
            corrected_array = ShiftIt.evaluate_shift_for_input_array(image_array)
            self.overwrite_original(x, corrected_array)

    def overwrite_original(self, file_name, array):
        print("overwriting original file..: ", file_name)
        np.savetxt(file_name[:-4] + ".txt", array, delimiter=' ',
                   header='string', comments='',
                   fmt='%s')


class BatchCalibration:
    def __init__(self, calibration_file_path, file_path):
        self.calibration_parameter = basic_file_app.load_1d_array(calibration_file_path, 0, 0)
        print(self.calibration_parameter, 'used calibration_files')
        self.file_path = file_path

    def calibrate_array(self):
        self.file_list = basic_file_app.get_file_list(self.file_path)
        my_calibration = calibration_analytical_from_array.CalibrateArray(self.calibration_parameter)
        for x in self.file_list:
            my_array = basic_file_app.load_2d_array(self.file_path + x, 0, 1, 2)
            my_calibration.set_input_array(my_array, x)
            my_calibration.main()
            my_calibration.save_data("back: " + path_background + "RZP-structure:___" + rzp_structure_name, roi_list)




path_background = "data/stray_light/945ms_straylight/"
name_background = path_background
path_picture = "data/A9_Lrot56_105ms_Gonio1460/LT18350/raw/"

# roi on image ( [x1, y1, x2, y2])
roi_list = ([0, 380, 1730, 1670])

emission_lines = basic_file_app.load_1d_array("calibration_files/Fe_XPL_detected_20210202.txt", 1, 3)

# px size in um, angle alpha degree, d in nm, angle beta in degree, distance RZP - Chip, offset in px
# is now given via read in txt - should look like this:
#rzp_structure_parameter = np.array([1.350e-02, 2.130e+00, 1.338e+03, 3.714e+00, 2.479e+03, 0.000e+00])

laser_gate_time_data = 105  # ms
per_second_correction = 1000 / laser_gate_time_data
rzp_structure_name = "RZPA9-S3_" + str(laser_gate_time_data) + "ms"

# create input pictures

file_list_background = basic_image_app.get_file_list(path_background)
batch_background = basic_image_app.ImageStackMeanValue(file_list_background, path_background)
my_background = batch_background.average_stack()
my_y_limit = 3.3E7

# reference positions (px) for minimum in roi for px shift evaluation
reference_point_list = [949, 987]
# path_binned_array_files to be opened for px-shifted arrays (usually excecution path for this python routine)
# Test = PxCorrectionOnStack(path_picture, reference_point_list)
# Test.px_shift(path_binned_array_files)

binned_file_path = "data/A9_Lrot56_105ms_Gonio1460/LT18350/px_shifted_cal/binned/"
calibration_path = "data/A9_Lrot56_105ms_Gonio1460/LT18350/A9_Lrot56_105ms_Gonio1460_LT18350_cal.txt"
calibration = BatchCalibration(calibration_path, binned_file_path)
calibration.calibrate_array()

plt.show()
