import hashlib
import struct
import datetime

#Bitcoin Blockchain protocol
int_size = 4
block_header_size = 80
sha256_size = 32
witness_flag_size = 2 # optional data
value_size = 8
#--------------------------

#SHA family uses Big-Endian format
def sha256_double(x):
    x = hashlib.sha256(hashlib.sha256(x).digest()).digest()
    return x

def read_little_endian(f, bytes):
    bytes = f.read(bytes)
    return bytes[::-1]

def hexify_bytes(val):
    if isinstance(val, bytes): return val.hex()
    else: return hex(val)

def unpack_one(format, bytes, obj = None):
    if obj: obj.raw_bytes += bytes
    return struct.unpack(format, bytes)[0]

# Please, pay attention that Merkle Tree implementations may vary, this one is used in Bitcoin
def get_merkle_root(txs):
    if len(txs) == 0:
        return bytes()
    
    while len(txs) > 1:   
        temp_list = []
        for idx in range(0, len(txs), 2):
            nl, nr = txs[idx], txs[idx]
            if idx != len(txs)-1:
                nr = txs[idx+1]
            temp_list.append(sha256_double(nl + nr))
        txs = temp_list
        
    return txs[0]

#read variable-length integer
def read_vli(fin, obj = None):
    bytes = fin.read(1)
    var_int = ord(bytes)
    if var_int <= 0xfc:
        if obj: obj.raw_bytes += bytes
        return var_int
    elif var_int == 0xfd:
        return unpack_one("<H", f.read(2), obj)
    elif var_int == 0xfe:
        return unpack_one("<I", f.read(4), obj)
    elif var_int == 0xff:
        return unpack_one("<Q", f.read(8), obj)

class BlockHeader:
    def read(self, fin, fout):
        #Compute blockheader hash - SHA256(SHA256(block_header)) with OPENSSL
        bytes = sha256_double(fin.read(block_header_size))
        cur_block_hash = hexify_bytes(bytes[::-1])
        fin.seek(-block_header_size, 1)

        #Version
        version_number = unpack_one('<I', fin.read(int_size))

        #Previous-block hash
        previous_block_hash = hexify_bytes(read_little_endian(fin, sha256_size))

        #Merkle-root
        merkle_root = read_little_endian(fin, sha256_size)
        #Save merkle-root hash value as a field for the block validation later
        self.merkle_root = merkle_root[::-1]

        #Timestamp, bits, nonce
        vals = struct.unpack('<3I', fin.read(int_size*3))

        fout.write('Current block hash= {}\n'.format(cur_block_hash))
        fout.write('Block version= {}\n'.format(version_number))
        fout.write('Previous block hash= {}\n'.format(previous_block_hash))
        fout.write('Merkle root= {}\n'.format(hexify_bytes(merkle_root)))
        creationTime = datetime.datetime.fromtimestamp(vals[0]).strftime('%d.%m.%Y %H:%M')
        fout.write('Time stamp= {}\n'.format(creationTime))
        fout.write('Bits= {}\n'.format(vals[1]))
        fout.write('Nonce= {}\n'.format(vals[2]))

class Transaction:
    class InputTx:
        def read(self, fin, fout, obj):
            #Previous Transaction hash
            bytes = read_little_endian(fin, sha256_size)
            pre_tx_hash = hexify_bytes(bytes)
            obj.raw_bytes += bytes[::-1]

            #Previous Txout-index
            txout_index = unpack_one('<I', fin.read(int_size), obj)

            #Txin-script length
            script_length = read_vli(fin, obj)

            #Read txin-script
            bytes = fin.read(script_length)
            script = hexify_bytes(bytes)
            obj.raw_bytes += bytes

            #Sequence number
            sequence_number = unpack_one('<I', fin.read(int_size), obj)

            fout.write('Txin previous hash= {}\n'.format(pre_tx_hash))
            fout.write('Txin previous id= {}\n'.format(hexify_bytes(txout_index)))
            fout.write('Txin script-length= {}\n'.format(script_length))
            fout.write('Txin script= {}\n'.format(script))
            fout.write('Sequence number= {}\n'.format(sequence_number))
    class OutputTx:
        def read(self, fin, fout, obj):
            #value non negative integer giving the number of Satoshis(BTC/10^8) to be transfered
            value = unpack_one('<Q', fin.read(value_size), obj)

            #Txout-script length
            script_length = read_vli(fin, obj)

            #Read txout-script
            bytes = fin.read(script_length)
            script = hexify_bytes(bytes)
            obj.raw_bytes += bytes

            fout.write('Txout satoshi amount= {}\n'.format(hexify_bytes(value)))
            fout.write('Txout script-length= {}\n'.format(script_length))
            fout.write('Txout script= {}\n'.format(script))
    def read(self, fin, fout):
        self.raw_bytes = b''

        #TX version number
        tx_version = unpack_one('<i', fin.read(int_size), self)
        fout.write('TX version= {}\n'.format(tx_version))

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
            fout.write('------Input tx{}---------------\n'.format(idx))
            in_tx = Transaction.InputTx()
            in_tx.read(fin, fout, self)
            fout.write('-------------------------------\n')
        #Out tx counter, variable length integer
        out_count = read_vli(fin, self)
        fout.write('Output tx count= {}\n'.format(out_count))

        #Read all output transactions
        for idx in range(out_count):
            fout.write('------Output tx{}--------------\n'.format(idx))
            out_tx = Transaction.OutputTx()
            out_tx.read(fin, fout, self)
            fout.write('-------------------------------\n')
        # Witnesses	A list of witnesses, 1 for each input, omitted if flag above is missing
        # Witness data isn't counted when calculating transaction hash
        if witness_flag:
            for i in range(in_count):
                tx_witnesses_amount = read_vli(fin)
                for j in range(tx_witnesses_amount):
                    cur_witness_len = read_vli(fin)
                    cur_witness_data = hexify_bytes(fin.read(witness_item_len))
                    fout.write('Witness[{},{},{}]:\n'.format(i,j,cur_witness_len))
                    fout.write('Witness data= {}\n'.format(cur_witness_data))

        #Lock-time if non-zero and sequence numbers are < 0xFFFFFFFF: block height or timestamp when transaction is final
        lock_time = unpack_one('<I', fin.read(int_size), self)
        if lock_time < 0x1DCD6500:
            fout.write('Lock time(block height)= {}\n'.format(lock_time))
        else:
            lock_time = datetime.datetime.fromtimestamp(lock_time).strftime('%d.%m.%Y %H:%M')
            fout.write('Lock time(timestamp)= {}\n'.format(lock_time))

        # Double hash this transaction SHA-256
        self.raw_bytes = sha256_double(self.raw_bytes)
        fout.write('Full transaction hash= {}\n'.format(hexify_bytes(self.raw_bytes)))

class Block:
    def read(self, fin, fout):
        #Magic number
        magic_number = unpack_one('<I', fin.read(int_size))
        while magic_number != 0xD9B4BEF9:
            #Skipping partially downloaded blocks
            magic_number = unpack_one('<I', fin.read(int_size))

        #Block size
        block_size = unpack_one('<I', fin.read(int_size))
        
        fout.write('Magic number= {}\n'.format(magic_number))
        fout.write('Block size= {}\n'.format(block_size))

        header = BlockHeader()
        header.read(fin, fout)
        
        #Transaction_counter - variable length(1-9 bytes)
        transaction_counter = read_vli(fin)
        fout.write('Transactions amount= {}\n\n'.format(transaction_counter))

        #Store transaction hashes to compute the merkle root and verify if parsed data is valid
        tx_hashes = []
        for idx in range(transaction_counter):
            fout.write('Transaction{}\n'.format(idx))
            tx = Transaction()
            tx.read(fin, fout)
            fout.write('\n')
            tx_hashes.append(tx.raw_bytes)

        # Compare header.merkle_root with root computed from tx_hashes
        merkle_root = get_merkle_root(tx_hashes)
        if merkle_root != header.merkle_root:
            fout.write('Merkle root mismatch - Expected{{}}, Actual{{}}'.format(header.merkle_root, merkle_root))

def get_net(magic_number):
    network = None
    if(magic_number == 3652501241): network = 'main network'
    elif(magic_number == 3669344250): network = 'test network'
    elif(magic_number == 118034699): network = 'test network 3'
    elif(magic_number== 4273258233): network = 'namecoin network'
    return network

def built_block_chain(headers_map, last_block_header):
    if len(headers_map) > 0 and last_block_header is not None:
        headers_count = 0
        cur_header = last_block_header
        while cur_header:
            cur_header = headers_map.get(cur_header.prev_block_hash)
            headers_count += 1
        # Found headers_count blocks and skipped len(headers_map)-headers_count orphan blocks
        ordered_headers = [None]*headers_count
        cur_header = last_block_header
        while cur_header:
            ordered_headers[headers_count-1] = cur_header
            cur_header = headers_map.get(cur_header.prev_block_hash)
            headers_count -= 1
        return ordered_headers
    else: return None