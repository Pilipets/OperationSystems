import os.path as path
import os
import re
import logging
from BitcoinProto import *

class BitcoinBlockchainParser:
    blk_pattern = re.compile('blk\d{5}.dat')
    logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(message)s', level=logging.DEBUG)

    def __init__(self, in_dir_path, out_dir_path):
        self.in_dir_path = in_dir_path
        self.out_dir_path = out_dir_path

        if not path.exists(in_dir_path):
            logging.error("Path(%s) to blk files doesn't exist", in_dir_path)
            raise FileNotFoundError("Path to blk files doesn't exist")
        if not path.exists(out_dir_path):
            logging.info("Path(%s) to output directory doesn't exist - creating one", out_dir_path)
            os.makedirs(out_dir_path)

    def parse(self):
        blk_files_list = os.listdir(self.in_dir_path)
        filter_func = lambda f: BitcoinBlockchainParser.blk_pattern.match(f)
        blk_files_list = list(filter(filter_func, blk_files_list))
        blk_files_list.sort()
        block_num = 0
        for blk_path in blk_files_list:
            in_path = self.in_dir_path + blk_path
            out_path = self.out_dir_path + blk_path[:9] + 'out'
            f_size = os.path.getsize(in_path)

            fin = open(in_path, 'rb')
            fout = open(out_path, 'w')
            logging.info("Started reading %s", in_path)
            while fin.tell() != f_size:
                try:
                    fout.write('------------Started reading block{}----------\n'.format(block_num))
                    blk = Block()
                    blk.read(fin, fout)
                    fout.write('------------Finished reading block{}---------\n\n'.format(block_num))
                    block_num += 1
                except IOError:
                    fout.write('Corrupted block in block{}, file={}\n'.format(block_num, in_path))
                    logging.warn("Corrupted data in %s, skipping to next block", in_path)
                    break
            logging.info("Finished reading %s", in_path)
            fin.close()
            fout.close()

        def parse_threaded(self):
            pass