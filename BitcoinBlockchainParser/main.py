from BlockchainParser import *
import time

if __name__ == '__main__':
    obj = BitcoinBlockchainParser("input/", "output/")
    start_time = time.time()
    obj.parse_multi_thread(10)
    print("--- %s seconds ---" % (time.time() - start_time))