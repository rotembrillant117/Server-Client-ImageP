from abc import abstractmethod, ABC
import numpy as np
import cv2

IMG_EXTENSIONS = {".PNG", ".jpg"}
VID_EXTENSIONS = {".mp4"}

class Transformation(ABC):
    def __init__(self, file_names, files_bytes, files_extensions):
        self.file_names = file_names
        self.files_extensions = files_extensions
        self.files_bytes = files_bytes
    @abstractmethod
    def transform(self):
        pass

class GrayScale(Transformation):
    def __init__(self, file_names, files_bytes, files_extensions):
        super().__init__(file_names, files_bytes, files_extensions)

    def transform(self):
        if self.files_extensions[0] in IMG_EXTENSIONS:
            self.handle_img()
        else:
            self.handle_mp4()

    def handle_img(self):
        image = np.asarray(bytearray(self.files_bytes[0]), dtype="uint8")
        image = cv2.imdecode(image, 0)
        # saves image to current directory
        cv2.imwrite(self.file_names[0], image)

    def handle_mp4(self):
        file = open(self.file_names[0], "wb")
        file.write(self.files_bytes[0])
        file.close()
        cap = cv2.VideoCapture(self.file_names[0])
        width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = cap.get(cv2.CAP_PROP_FPS)
        vid_writer = cv2.VideoWriter("output.mp4", cv2.VideoWriter_fourcc(*'mp4v'), fps, (width, height),
                                     isColor=False)
        for fr_index in range(int(cap.get(cv2.CAP_PROP_FRAME_COUNT))):
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            vid_writer.write(gray)
        cap.release()
        vid_writer.release()

