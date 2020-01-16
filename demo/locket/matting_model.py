import os
import numpy as np
from PIL import Image
import tensorflow as tf

class DeepLabModel(object):
    INPUT_TENSOR_NAME = 'ImageTensor:0'
    OUTPUT_TENSOR_NAME = 'SemanticPredictions:0'
    INPUT_SIZE = 513
    FROZEN_GRAPH_NAME = 'frozen_inference_graph'

    def __init__(self, path):
        self.graph = tf.Graph()

        graph_def = None
        with tf.gfile.GFile(path, 'rb')as file_handle:
            graph_def = tf.GraphDef.FromString(file_handle.read())

        if graph_def is None:
            raise RuntimeError('Cannot find inference graph in tar archive.')

        with self.graph.as_default():
            tf.import_graph_def(graph_def, name='')

        self.sess = tf.Session(graph=self.graph)

    def run(self, image):
        """Runs inference on a single image.

        Args:
            image: A PIL.Image object, raw input image.

        Returns:
            resized_image: RGB image resized from original input image.
            seg_map: Segmentation map of `resized_image`.
        """
        width, height = image.size
        resize_ratio = 1.0 * self.INPUT_SIZE / max(width, height)
        target_size = (int(resize_ratio * width), int(resize_ratio * height))
        resized_image = image.convert('RGB').resize(target_size, Image.ANTIALIAS)
        batch_seg_map = self.sess.run(
            self.OUTPUT_TENSOR_NAME,
            feed_dict={self.INPUT_TENSOR_NAME: [np.asarray(resized_image)]})
        seg_map = batch_seg_map[0]
        return resized_image, seg_map

class DeepLab_Matting(object):
    def __init__(self, path):
        self.MODEL = DeepLabModel(path)
        print('model loaded successfully!')

    def run(self, path):
        img = Image.open(path)
        resized_im, seg_map = self.MODEL.run(img)
        img_arr = np.array(resized_im)
        res_arr = np.concatenate((img_arr, np.expand_dims(seg_map, -1)), -1).astype(np.uint8)
        return res_arr


# if __name__ == "__main__":
#     matting = DeepLab_Matting('/home/celbree/MattingHuman/deeplab_custom/exp/save/model.pb')
#     res = matting.run('/home/celbree/MattingHuman/deeplab_custom/dataset/test.jpg')