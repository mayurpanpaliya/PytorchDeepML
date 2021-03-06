
import os

import numpy as np
import pandas as pd
from PIL import Image
import torch
from torch.utils.data import Dataset


class ImageRowDataFrameDataset(Dataset):
    """ Class useful for reading images from a dataframe.
        Each row is assume to be the flattened array of an image.
        Each row is then reshaped to the provided image_size.
    """
    def __init__(self, dataframe:pd.DataFrame, target_column=None, image_size=(28, 28),
                 transform=None):
        self.dataframe = dataframe.reset_index(drop=True, inplace=False)
        self.target_column = None

        if target_column is not None:
            self.target_column = self.dataframe[target_column]
            self.dataframe.drop(target_column, axis=1, inplace=True)

        self.samples = self.dataframe.shape[0]
        self.image_size = image_size
        self.transform = transform

    def __getitem__(self, index):

        X = self.dataframe.iloc[index]

        X = Image.fromarray(X.to_numpy().reshape(self.image_size).astype(np.uint8))
        if self.transform is not None:
            X = self.transform(X)

        y = 0
        if self.target_column is not None:
            y = self.target_column.loc[index]

        return X, y

    def __len__(self):
        return self.samples


class ImageFileDataFrameDataset(Dataset):
    """ This class is useful for reading dataset of images for image classification/regression problem.
    """
    def __init__(self, dataframe, img_file_path_column='image', target_column=None,
                 image_dir=None, transforms=None, open_file_func=None):

        self.dataframe = dataframe.reset_index(drop=True, inplace=False)
        self.img_file_path_column = img_file_path_column
        self.target_column = target_column
        self.image_dir = image_dir
        self.transforms = transforms
        self.samples = self.dataframe.shape[0]
        self.open_file_func = open_file_func

    def __len__(self):
        return self.samples

    def __getitem__(self, index):

        image_file = self.dataframe.loc[index, self.img_file_path_column]

        if self.image_dir is not None:
            image_file = os.path.join(self.image_dir, image_file)

        if self.open_file_func is None:
            X = Image.open(image_file)
        else:
            X = self.open_file_func(image_file)

        y = 0
        if self.target_column is not None:
            y = self.dataframe.loc[index, self.target_column]

        if self.transforms is not None:
            X = self.transforms(X)

        return X, y


class ImageListDataset(Dataset):

    def __init__(self, image_dir, transforms=None, open_file_func=None):

        self.image_dir = image_dir
        self.images = os.listdir(image_dir)
        self.transforms = transforms
        self.open_file_func = open_file_func

    def __len__(self):
        return len(self.images)

    def __getitem__(self, index):

        image_file = self.images[index]
        if self.open_file_func is None:
            X = Image.open(os.path.join(self.image_dir, image_file))
        else:
            X = self.open_file_func(os.path.join(self.image_dir, image_file))

        if self.transforms is not None:
            X = self.transforms(X)

        return X, image_file


class SemSegImageFileDataFrameDataset(Dataset):
    """ This class is useful for reading images and mask labels required for
        semantic segmentation problems.

        The image file and corresponding mask label file should have the same name,
        and should be stored in a provided mask directory.

        You can provide custom open_file_func for reading image, by it uses PIL Image.open()

    """
    def __init__(self, dataframe, image_dir, mask_dir, transforms=None, open_file_func=None):
        self.dataframe = dataframe.reset_index(drop=True, inplace=False)
        self.image_dir = image_dir
        self.mask_dir = mask_dir
        self.transforms = transforms
        self.samples = self.dataframe.shape[0]
        self.open_file_func = open_file_func

    def __len__(self):
        return self.samples

    def __getitem__(self, index):
        image_file = self.dataframe.loc[index, 'image']

        if self.open_file_func is None:
            image = Image.open(os.path.join(self.image_dir, image_file))
            mask = Image.open(os.path.join(self.mask_dir, image_file))
        else:
            image = self.open_file_func(os.path.join(self.image_dir, image_file))
            mask = self.open_file_func(os.path.join(self.mask_dir, image_file))

        if self.transforms is not None:
            image, mask = self.transforms(image=image, mask=mask)

        return image, mask