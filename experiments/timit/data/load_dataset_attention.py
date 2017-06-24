#! /usr/bin/env python
# -*- coding: utf-8 -*-

"""Load dataset for the Attention model (TIMIT corpus).
   You can use the multi-GPU version.
"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from os.path import join
import pickle
import numpy as np

from utils.progressbar import wrap_iterator
from utils.data.attention_all_load import DatasetBase


class Dataset(DatasetBase):

    def __init__(self, data_type, label_type, batch_size, eos_index,
                 is_sorted=True, is_progressbar=False, num_gpu=1):
        """A class for loading dataset.
        Args:
            data_type: string, train or dev or test
            label_type: string, phone39 or phone48 or phone61 or character
            eos_index: int , the index of <EOS> class
            is_sorted: if True, sort dataset by frame num
            is_progressbar: if True, visualize progressbar
            num_gpu: int, if more than 1, divide batch_size by num_gpu
        """
        if data_type not in ['train', 'dev', 'test']:
            raise ValueError('data_type is "train" or "dev" or "test".')

        self.data_type = data_type
        self.label_type = label_type
        self.batch_size = batch_size * num_gpu
        self.eos_index = eos_index
        self.is_sorted = is_sorted
        self.is_progressbar = is_progressbar
        self.num_gpu = num_gpu

        self.input_size = 123
        self.dataset_path = join(
            '/n/sd8/inaguma/corpus/timit/dataset/attention/',
            label_type, data_type)

        # Load the frame number dictionary
        with open(join(self.dataset_path, 'frame_num.pickle'), 'rb') as f:
            self.frame_num_dict = pickle.load(f)

        # Sort paths to input & label by frame num
        frame_num_tuple_sorted = sorted(self.frame_num_dict.items(),
                                        key=lambda x: x[1])
        input_paths, label_paths = [], []
        for input_name, frame_num in frame_num_tuple_sorted:
            input_paths.append(join(
                self.dataset_path, 'input', input_name + '.npy'))
            label_paths.append(join(
                self.dataset_path, 'label', input_name + '.npy'))
        self.input_paths = np.array(input_paths)
        self.label_paths = np.array(label_paths)
        self.data_num = len(self.input_paths)

        # Load all dataset in advance
        print('=> Loading ' + data_type + ' dataset (' + label_type + ')...')
        input_list, label_list = [], []
        for i in wrap_iterator(range(self.data_num), self.is_progressbar):
            input_list.append(np.load(self.input_paths[i]))
            label_list.append(np.load(self.label_paths[i]))
        self.input_list = np.array(input_list)
        self.label_list = np.array(label_list)

        self.rest = set([i for i in range(self.data_num)])
