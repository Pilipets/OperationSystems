from BlockchainParser import *

if __name__ == '__main__':
    obj = BitcoinBlockchainParser("input/", "output/")
    obj.parse()