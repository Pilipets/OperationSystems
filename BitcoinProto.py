import hashlib
import struct

#Bitcoin Blockchain protocol
int_size = 4
block_header_size = 80
sha256_size = 32
witness_flag_size = 2 # optional data
value_size = 8
#--------------------------

def read_little_endian(f, bytes):
    bytes = f.read(bytes)
    return bytes[::-1]

def hexify_bytes(val):
    if isinstance(val, bytes):
        return val.hex().upper()
    else:
        return hex(val).upper()
def unpack_one(format, bytes, obj = None):
    if obj: obj.raw_bytes += bytes
    return struct.unpack(format, bytes)[0]

# https://github.com/bitcoin/bitcoin/blob/master/src/consensus/merkle.cpp
# Compute only merkle root value exactly the same way as Bitcoin does
# Please, pay attention that Merkle Tree implementations may vary, this one is used in Bitcoin
def get_merkle_root(tx_list):
    if len(tx_list) == 0:
        return bytes()

    #Traditional double sha256 hashing
    sha256_double = lambda x: hashlib.sha256(hashlib.sha256(x).digest()).digest()
    while len(tx_list) != 1:
        #Make a tx_list len even
        if len(tx_list)&1: tx_list.append(tx_list[-1])
        temp_list = []
        for idx in range(0, len(tx_list), 2):
            h1, h2 = tx_list[idx][::-1], tx_list[idx+1][::-1]
            temp_list.append(sha256_double(h1+h2)[::-1])
        tx_list = temp_list
    return tx_list[0]

#read variable-length integer https://bitcointalk.org/index.php?topic=32849.msg410480#msg410480
def read_vli(fin, obj = None):
    bytes = fin.read(1)
    var_int = ord(bytes)
    if var_int <= 0xfc:
        if obj: obj.raw_bytes += bytes
        return var_int
    elif var_int == 0xfd:
        return unpack_one("<xH", f.read(2), obj)
    elif var_int == 0xfe:
        return unpack_one("<xI", f.read(4), obj)
    elif var_int == 0xff:
        return unpack_one("<xQ", f.read(8), obj)

class BlockHeader:
    def read(self, fin, fout):
        #Compute blockheader hash - SHA256(SHA256(block_header)) with OPENSSL
        bytes = fin.read(block_header_size)
        #SHA family uses Big-Endian format
        bytes = hashlib.sha256(bytes).digest()
        bytes = hashlib.sha256(bytes).digest()
        cur_block_hash = hexify_bytes(bytes[::-1]) # Back to Little-Endian format bytes[::-1]
        fout.write('SHA-256 Current block hash= {}\n'.format(cur_block_hash))
        fin.seek(-block_header_size, 1)

        #Version
        version_number = unpack_one('<I', fin.read(int_size))
        fout.write('Version number= {}\n'.format(version_number))

        #Previous-block hash
        previous_block_hash = hexify_bytes(read_little_endian(fin, sha256_size))
        fout.write('SHA-256 Previous block hash= {}\n'.format(previous_block_hash))

        #Merkle-root
        merkle_root = read_little_endian(fin, sha256_size)
        fout.write('Merkle root hash= {}\n'.format(hexify_bytes(merkle_root)))
        #Save merkle-root hash value as a field for validation in the block
        self.merkle_root = merkle_root

        #Timestamp, difficulty, nonce
        vals = struct.unpack('<3I', fin.read(int_size*3))
        fout.write('Time stamp= {}\n'.format(hexify_bytes(vals[0])))
        fout.write('Difficulty= {}\n'.format(hexify_bytes(vals[1])))
        fout.write('Nonce= {}\n'.format(hexify_bytes(vals[2])))

class Transaction:
    class InputTx:
        def read(self, fin, fout, obj):
            #Previous Transaction hash
            bytes = read_little_endian(fin, sha256_size)
            pre_tx_hash = hexify_bytes(bytes)
            obj.raw_bytes += bytes[::-1]
            fout.write('TX from hash= {}\n'.format(pre_tx_hash))

            #Previous Txout-index
            txout_index = unpack_one('<I', fin.read(int_size), obj)
            fout.write('TX output= {}\n'.format(hexify_bytes(txout_index)))

            #Txin-script length
            script_length = read_vli(fin, obj)

            #Read txin-script
            bytes = fin.read(script_length)
            script = hexify_bytes(bytes)
            obj.raw_bytes += bytes
            fout.write('Input script= {}\n'.format(script))

            #Sequence number
            sequence_number = unpack_one('<I', fin.read(int_size), obj)
            fout.write('Sequence number= {}\n'.format(hexify_bytes(sequence_number)))
    class OutputTx:
        def read(self, fin, fout, obj):
            #value non negative integer giving the number of Satoshis(BTC/10^8) to be transfered
            value = unpack_one('<Q', fin.read(value_size), obj)
            fout.write('Satoshi amount= {}\n'.format(hexify_bytes(value)))

            #Txout-script length
            script_length = read_vli(fin, obj)

            #Read txout-script
            bytes = fin.read(script_length)
            script = hexify_bytes(bytes)
            obj.raw_bytes += bytes
            fout.write('Output script= {}\n'.format(script))

    def read(self, fin, fout):
        self.raw_bytes = b''

        #TX version number
        tx_version = unpack_one('<i', fin.read(int_size), self)
        fout.write('TX version number= {}\n'.format(tx_version))

        #Witness flag that might be absent 2 bytes(0x0001 if present)
        #Witness flag isn't counted when calculating transaction hash
        flag = unpack_one('>h', fin.read(witness_flag_size))

        #Witness flag is missed
        if flag != 1:
            witness_flag = False
            fin.seek(-witness_flag_size, 1)
        else:
            witness_flag = True

        #In tx counter, variable length integer
        in_count = read_vli(fin, self)
        fout.write('Input tx count= {}\n'.format(in_count))

        #Read all input transactions
        for idx in range(in_count):
            #fout.write('------Input tx{}---------------\n'.format(idx))
            in_tx = Transaction.InputTx()
            in_tx.read(fin, fout, self)
            #fout.write('-------------------------------\n')
        #Out tx counter, variable length integer
        out_count = read_vli(fin, self)
        fout.write('Output tx count= {}\n'.format(out_count))

        #Read all output transactions
        for idx in range(out_count):
            #fout.write('------Output tx{}--------------\n'.format(idx))
            out_tx = Transaction.OutputTx()
            out_tx.read(fin, fout, self)
            #fout.write('-------------------------------\n')
        # Witnesses	A list of witnesses, 1 for each input, omitted if flag above is missing
        # Witness data isn't counted when calculating transaction hash
        if witness_flag:
            for i in range(self.in_count):
                witness_len = read_vli(fin)
                for j in range(witness_len):
                    witness_item_len = read_vli(fin)
                    witness_data = hexify_bytes(fin.read(witness_item_len))
                    fout.write('Witness[{},{},{}]= {}'.format(i,j, witness_item_len, witness_data))

        #Lock-time if non-zero and sequence numbers are < 0xFFFFFFFF: block height or timestamp when transaction is final
        lock_time = unpack_one('<I', fin.read(int_size), self)
        fout.write('Lock time= {}\n'.format(hexify_bytes(lock_time)))

        # Double hash SHA-256, Big-Endian
        bytes = self.raw_bytes
        bytes = hashlib.sha256(bytes).digest()
        bytes = hashlib.sha256(bytes).digest()
        bytes = bytes[::-1] # Back to little-Endian
        fout.write('Full TX hash= {}\n'.format(hexify_bytes(bytes)))
        self.raw_bytes = bytes

class Block:
    def read(self, fin, fout):
        #Magic number
        magic_number = unpack_one('<I', fin.read(int_size))
        while magic_number != 0xD9B4BEF9:
            #Skipping partially downloaded blocks
            magic_number = unpack_one('<I', fin.read(int_size))
        fout.write('Magic number= {}\n'.format(hexify_bytes(magic_number)))

        #Block size
        block_size = unpack_one('<I', fin.read(int_size))
        fout.write('Block size= {}\n'.format(hexify_bytes(block_size)))

        #Transaction counter
        header = BlockHeader()
        header.read(fin, fout)
        
        #Transaction_counter - variable length(1-9 bytes)
        transaction_counter = read_vli(fin)
        fout.write('Transactions amount= {}\n\n'.format(transaction_counter))

        #Store transaction hashes to compute the merkle root and verify if parsed data is valid
        tx_hashes = []
        for idx in range(transaction_counter):
            #fout.write('Transaction{}\n'.format(idx))
            tx = Transaction()
            tx.read(fin, fout)
            fout.write('\n')
            tx_hashes.append(tx.raw_bytes)

        # Compare header.merkle_root with root computed from tx_hashes
        merkle_root = get_merkle_root(tx_hashes)
        if merkle_root != header.merkle_root:
            fout.write('Merkle root mismatch - Expected{{}}, Actual{{}}'.format(header.merkle_root, merkle_root))