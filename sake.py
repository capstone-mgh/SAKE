import dicom
import os
import numpy as np
from scipy.ndimage import gaussian_filter, label, find_objects, binary_propagation
from skimage.measure import find_contours, points_in_poly


class Sake:

	def __init__(self, path):
		self.imagePath = path
		self.imageArray = None
		self.loadSeries(path)

	def loadSeries(self, path):
		self.imagePath = path
		# read from the URL. Right now this is local path

		lstFilesDCM = []  # create an empty list
		for dirName, subdirList, fileList in os.walk(self.imagePath):
			for filename in fileList:
				if ".dcm" in filename.lower():  # check whether the file's DICOM
					lstFilesDCM.append(os.path.join(dirName,filename))

		# Get ref file
		RefDs = dicom.read_file(lstFilesDCM[0])

		# Load dimensions based on the number of rows, columns, and slices (along the Z axis)
		ConstPixelDims = (len(lstFilesDCM), int(RefDs.Rows), int(RefDs.Columns))

		# Load spacing values (in mm)
		ConstPixelSpacing = (float(RefDs.PixelSpacing[0]), float(RefDs.PixelSpacing[1]), 1.)

		# The array is sized based on 'ConstPixelDims'
		self.imagesArray = np.zeros(ConstPixelDims, dtype=RefDs.pixel_array.dtype)

		# loop through all the DICOM files
		for filenameDCM in lstFilesDCM:
			# read the file
			ds = dicom.read_file(filenameDCM)
			# store the raw image data
			self.imagesArray[ds.InstanceNumber-1, :, :] = ds.pixel_array

		return self.imagesArray.shape

	def getImage(self, z):
		return self.imagesArray[z]

	def output_mask(self, y, x, image, tolerance=0.1):
		output = np.zeros_like(image)
		input_mask = np.zeros_like(image)
		input_mask[y,x] = 1
		tolerance *= np.max(image)
		greater = np.greater_equal(image, image[y,x] - tolerance)
		less = np.less_equal(image, image[y,x] + tolerance)
		return binary_propagation(input = input_mask, mask = greater*less)

	def segmentImage(self, z, y, x, threshold=0.1, x_bound=2000, y_bound=2000, max_size = 1000):
		x_offset = max(0, x - x_bound)
		y_offset = max(0, y - y_bound)
		x_bounding = slice(x_offset, min(self.imagesArray.shape[2], x + x_bound))
		y_bounding = slice(y_offset, min(self.imagesArray.shape[1], y + y_bound))
		bounding_slice = self.imagesArray[z, y_bounding, x_bounding]
		new_x = x - x_offset
		new_y = y - y_offset
		segmented_slice = self.output_mask(new_y, new_x, bounding_slice, threshold)
		area = len(np.where(segmented_slice == 1.)[0])
		# filter by max area
		if area > max_size:
			return None, None, None
		contour_slice = find_contours(segmented_slice, level=0.5)
		mask_offset = np.array([x_offset, y_offset])
		polygon = contour_slice[0] + mask_offset
		polygon = np.column_stack((polygon[:,1], polygon[:,0])) #convert to x,y
		return segmented_slice, mask_offset, polygon
