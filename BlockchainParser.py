import os.path as path
import os
import re
import logging
from BitcoinProto import *

class BitcoinBlockchainParser:
    blk_pattern = re.compile('blk\d{5}.dat')
    logging.basicConfig(format='%(asctime)s - %(message)s')

    def __init__(self, in_dir_path, out_dir_path):
        self.in_dir_path = in_dir_path
        self.out_dir_path = out_dir_path

        if not path.exists(in_dir_path):
            logging.error("Path(%s) to blk files doesn't exist", in_dir_path)
            raise FileNotFoundError("Path to blk files doesn't exist")
        if not path.exists(out_dir_path):
            logging.info("Path(%s) to output directory doesn't exist - creating one", out_dir_path)
            os.makedirs(out_dir_path)

    def parse(self, verbose = False):
        blk_files_list = os.listdir(self.in_dir_path)
        filter_func = lambda f: BitcoinBlockchainParser.blk_pattern.match(f)
        blk_files_list = list(filter(filter_func, blk_files_list))
        blk_files_list.sort()

        for blk_path in blk_files_list:
            blk_path = self.in_dir_path + blk_path
            f_ptr = open(blk_path, 'rb')
            f_size = os.path.getsize(blk_path)
            while(f_ptr.tell() != f_size):
                blk = Block()
                blk.read(f_ptr)
            f_ptr.close()