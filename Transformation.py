from abc import abstractmethod, ABC
import numpy as np
import cv2
import os
from constants import IMG_EXTENSIONS, VID_EXTENSIONS

class Transformation(ABC):
    """
    An abstract class of transformations that can be done on files
    """
    def __init__(self, file_names, files_bytes, files_extensions, directory):
        self.file_names = file_names
        self.files_extensions = files_extensions
        self.files_bytes = files_bytes
        self.directory = directory
    @abstractmethod
    def transform(self):
        """
        Performs the transformation on the specified files
        :return: tuple of (output_file, output_file extension)
        """
        pass

class GrayScale(Transformation):
    """
    This class performs an RGB to Gray-Scale transformation on image and video files (look at constants.py for the type
    of image and video extension available, i.e. IMG_EXTENSIONS, VID_EXTENSIONS)
    """
    def __init__(self, file_names, files_bytes, files_extensions, directory):
        super().__init__(file_names, files_bytes, files_extensions, directory)

    def transform(self):
        if self.files_extensions[0] in IMG_EXTENSIONS:
            return self.handle_img()
        else:
            return self.handle_mp4()

    def handle_img(self):
        """
        This function creates a Gray-Scale image from the given file
        :return:
        """
        image = np.asarray(bytearray(self.files_bytes[0]), dtype="uint8")
        image = cv2.imdecode(image, 0)
        # saves image to current directory
        cv2.imwrite(os.path.join(self.directory, self.file_names[0]), image)
        return self.file_names[0], self.files_extensions[0]

    def handle_mp4(self):
        """
        This function creates a Gray-Scale .mp4 video from the given file
        :return:
        """
        file_to_open = os.path.join(self.directory, self.file_names[0])
        file = open(file_to_open, "wb")
        file.write(self.files_bytes[0])
        file.close()
        new_name = f"output{self.file_names[0]}"
        directory = os.path.join(self.directory, new_name)
        cap = cv2.VideoCapture(file_to_open)
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        vid_writer = cv2.VideoWriter(directory, cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height),
                                     isColor=False)
        for fr_index in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vid_writer.write(gray)
        cap.release()
        vid_writer.release()
        return new_name, self.files_extensions[0]


class PyramidBlend(Transformation):
    """
    This class performs a Pyramid Blend transformation on two images (look at constants.py for the type
    of image extensions available, i.e. IMG_EXTENSIONS)
    """
    def __init__(self, file_names, files_bytes, files_extensions, directory):
        super().__init__(file_names, files_bytes, files_extensions, directory)

    def transform(self):
        for i in range(2):
            file = open(os.path.join(self.directory, self.file_names[i]), "wb")
            file.write(self.files_bytes[i])
            file.close()
        img1 = cv2.imread(os.path.join(self.directory, self.file_names[0]))
        img1 = cv2.resize(img1, (1000, 1000))
        img2 = cv2.imread(os.path.join(self.directory, self.file_names[1]))
        img2 = cv2.resize(img2, (1000, 1000))
        gauss_pyr_1 = self.create_gaussian_pyramid(img1)
        gauss_pyr_2 = self.create_gaussian_pyramid(img2)
        laplac_pyr_1 = self.create_laplacian_pyramid(gauss_pyr_1)
        laplac_pyr_2 = self.create_laplacian_pyramid(gauss_pyr_2)
        blended = self.create_blended(laplac_pyr_1, laplac_pyr_2)
        cv2.imwrite(os.path.join(self.directory, self.file_names[0]), blended)
        return self.file_names[0], self.files_extensions[0]

    def create_gaussian_pyramid(self, image):
        """
        This function creates the Gaussian pyramid of an image
        :param image: the image
        :return: gaussian_pyramid
        """
        layer = image.copy()
        gaussian_pyramid = [layer]
        for i in range(6):
            layer = cv2.pyrDown(layer)
            gaussian_pyramid.append(layer)
        return gaussian_pyramid
    def create_laplacian_pyramid(self, gaussian_pyramid):
        """
        This functon creates the Laplacian pyramid from the given Gaussian pyramid
        :param gaussian_pyramid: the Gaussian pyramid
        :return: laplacian_pyramid
        """
        layer = gaussian_pyramid[5]
        laplacian_pyramid = [layer]
        for i in range(5, 0, -1):
            size = (gaussian_pyramid[i - 1].shape[1], gaussian_pyramid[i - 1].shape[0])
            gaussian_expanded = cv2.pyrUp(gaussian_pyramid[i], dstsize=size)
            laplacian = cv2.subtract(gaussian_pyramid[i - 1], gaussian_expanded)
            laplacian_pyramid.append(laplacian)
        return laplacian_pyramid

    def create_blended(self, laplac_pyr_1, laplac_pyr_2):
        """
        This function creates the desired blended image
        :param laplac_pyr_1: Laplacian pyramid of image 1
        :param laplac_pyr_2: Laplacian pyramid of image 2
        :return: blended image
        """
        blended_pyramid = []
        n = 0
        for img1_lap, img2_lap in zip(laplac_pyr_1, laplac_pyr_2):
            n += 1
            cols, rows, ch = img1_lap.shape
            laplacian = np.hstack((img1_lap[:, 0:int(cols / 2)], img2_lap[:, int(cols / 2):]))
            blended_pyramid.append(laplacian)

        blended_reconstructed = blended_pyramid[0]
        for i in range(1, 6):
            size = (blended_pyramid[i].shape[1], blended_pyramid[i].shape[0])
            blended_reconstructed = cv2.pyrUp(blended_reconstructed, dstsize=size)
            blended_reconstructed = cv2.add(blended_pyramid[i], blended_reconstructed)

        return blended_reconstructed