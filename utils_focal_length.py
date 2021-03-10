# %% Definition of Classes and Functions
# value in mm is named without 'px'
# value in pixel is named with 'px'
import os
import pandas as pd
import numpy as np


def get_path():
    basepath = os.path.abspath(__file__)
    current_path = os.path.dirname(basepath)
    return current_path


f = open(os.path.join(get_path(), 'cameraSensors.db'))

CAMSENSORDB = pd.read_csv(f,
                          names=['make', 'model', 'ccd_width', 'providers'],
                          header=None, sep=';')


class focal_length_helper:
    '''A class for obtaining related informations about focal length

    Attributes:
        db_path: the path of the db file
        img_path: the path of img
        fl: focal length in mm
        equivalent_fl: equvalent focal length in 35mm
        img_width_px: image width in pixel
        img_height_px: image height in pixel
    '''

    def __init__(self, img_path):
        super().__init__()
        self.img_path = img_path
        self.fl, self.efl, self.img_width_px, self.img_height_px, self.make, self.model = self.obtain_exif_exif(
            img_path)

    def _ccd_width_db(self):
        """obtain ccd width based on make and model information in camera sensors database

        Return:
            ccd_width: ccd width in mm
        """
        df = CAMSENSORDB
        import re
        self.make = str.split(self.make)[0]
        # print(self.make, self.model)
        df = df[df['make'].str.contains(self.make, flags=re.IGNORECASE)]
        df = df[df['model'].str.contains(self.model, flags=re.IGNORECASE)]
        # print(df)
        self.ccd_width = df.iat[0, 2]  # the third column

    def _ccd_width_efl(self):
        """obtain ccd width based on equivalent focal length
            1. EFL = FL * 43.27 / \sqrt(ccd width^2+ccd height^2)
            2. ccd width/ccd height = image width/image height

        Return:
            ccd_width: ccd width in mm
        """
        ccd_diagonal = 43.27 / (self.efl / self.fl)
        self.ccd_width = np.sqrt(np.power(ccd_diagonal, 2) / (1 + np.power(self.img_height_px / self.img_width_px, 2)))

    def obtain_focal_length_px(self, method='db'):
        '''obtain focal length in pixel

        Attributes:
            image_path: the absolute path of the photo
            method: the method to obtrain focal length in pixel, now support 'db'(default) or 'efl'
        '''
        if method == 'db':
            self._ccd_width_db()
        elif method == 'efl':
            self._ccd_width_efl()
        fl_px = self.img_width_px * self.fl / self.ccd_width
        return fl_px

    def obtain_focal_length_mm(self):
        return self.fl

    def obtain_intrinsic_matrix(self, method='db'):
        '''Obtain the intrinsic matrix of a photo.

        Attributes:
            method: the method to obtain focal length in pixel, now support 'db'(default) or 'efl'

        Returns:
            k: an intrinsic matrix in numpy
        '''
        fl_px = self.obtain_focal_length_px(method)
        k = np.array([[fl_px, 0, self.img_width_px / 2], [0, fl_px, self.img_height_px / 2], [0, 0, 1]])
        return k

    def obtain_intrinsics(self, method='db'):
        '''Obtain the intrinsics of a photo.

        Attributes:
            method: the method to obtrain focal length in pixel, now support 'db'(default) or 'efl'

        Returns:
            fl_px: focal length in pixel
            u_0:
            v_0:
        '''
        fl_px = self.obtain_focal_length_px(method)
        u_0 = self.img_width_px / 2
        v_0 = self.img_height_px / 2
        return fl_px, u_0, v_0

    @staticmethod
    def obtain_exif_exif(img_path):
        '''Obtain exif using the pacakge exif. Install it using
        ```bash
        pip install exif
        ```
        Now is hided.
        '''
        from exif import Image
        with open(img_path, 'rb') as image_file:
            image = Image(image_file)
            if not image.has_exif:
                raise Exception('exif information is not exist!')
            # for tag in dir(image):
            #     print(tag, '=', image.get(tag))
            fl = image.focal_length
            equivalent_fl = image.focal_length_in_35mm_film
            img_width_px = image.pixel_x_dimension
            img_height_px = image.pixel_y_dimension
            make = image.make
            model = image.model
            return fl, equivalent_fl, img_width_px, img_height_px, make, model

    @staticmethod
    def __obtain_exif_exifread(img_path):
        '''Obtain exif using the pacakge exifread. Install it using
        ```bash
        pip install exifread
        ```
        '''
        import exifread
        with open(img_path, 'rb') as image_file:
            tags = exifread.process_file(image_file)
            # for key in tags.keys():
            #     print(key, '=', tags[key].values)
            fl = tags['EXIF FocalLength'].values[0].num / tags['EXIF FocalLength'].values[0].den
            equivalent_fl = tags['EXIF FocalLengthIn35mmFilm'].values[0]
            img_width_px = tags['EXIF ExifImageWidth'].values[0]
            img_height_px = tags['EXIF ExifImageLength'].values[0]
            make = tags['Image Make'].values
            model = tags['Image Model'].values
            return fl, equivalent_fl, img_width_px, img_height_px, make, model

    @staticmethod
    def extract_intrinsics_df(data_path, method='db'):
        '''Extract the intrinsics of photos in the data_path into a dataframe for analysis.

        Attributes:
            data_path: the absolute paths of photos
            method: the method to obtrain focal length in pixel, now support 'db'(default) or 'efl'
        
        Returns:
            A pands dataframe contains the pairs of filename and intrinsics
        '''
        df = pd.DataFrame(columns=['fl_px', 'u_0', 'v_0'], dtype=np.float16)
        index = 0
        for filename in os.listdir(data_path):
            file_path = os.path.join(data_path, filename)  # for every file
            # print(file_path)
            try:
                intrinsics = focal_length_helper(file_path).obtain_intrinsics(method)
                df.loc[index] = intrinsics  # add to the dataframe
                index += 1
            except (AttributeError, KeyError, IndexError) as e:
                # AttributeError, KeyError: when obtaining exif, some attributes are missing
                # IndexError: when make and model is not contained in camera sensors db 
                # print(e)
                continue
        return df
