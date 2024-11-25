import hashlib
import os
import secp256k1
import base58
import bech32
import math
import multiprocessing
from random import randint
import time

# Define the ORDER of the SECP256k1 curve
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Dynamically calculate partition size
def calculate_partition_size(address_count, partitions):
    partition_size = address_count // partitions
    return partition_size, address_count % partitions

# Load Bitcoin addresses into exact sets for each category and partition
def load_address_sets(filenames, partitions=10):
    categories = ['P2PKH', 'P2SH', 'Bech32']
    address_sets = []

    for partition_index in range(partitions):
        partition_set = {category: set() for category in categories}

        for category, filename in zip(categories, filenames):
            with open(filename, "r") as f:
                # Read addresses for this partition
                all_addresses = [line.strip() for line in f]
                partition_size, remainder = calculate_partition_size(len(all_addresses), partitions)
                start = partition_index * partition_size
                end = start + partition_size
                if partition_index == partitions - 1:  # Last partition takes the remainder
                    end += remainder

                addresses = all_addresses[start:end]
                partition_set[category].update(addresses)

            print(f"Partition {partition_index + 1}, Category {category}: Loaded {len(partition_set[category])} addresses.")

        address_sets.append(partition_set)

    return address_sets

# Convert a public key to different Bitcoin address formats
def public_key_to_addresses(public_key):
    sha256 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    p2pkh = base58.b58encode_check(b'\x00' + ripemd160).decode('utf-8')
    p2sh = base58.b58encode_check(b'\x05' + hashlib.new('ripemd160', hashlib.sha256(ripemd160).digest()).digest()).decode('utf-8')
    bech32_address = bech32.encode('bc', 0, ripemd160)
    return p2pkh, p2sh, bech32_address

# Generate a batch of random private keys within a range
def generate_random_private_keys_in_range(start, end, batch_size):
    for _ in range(batch_size):
        private_key_int = randint(start, end)
        yield private_key_int.to_bytes(32, 'big')

# Core brute-force logic
def try_private_keys_batch(start, end, num_keys, address_set_partition):
    keys = generate_random_private_keys_in_range(start, end, num_keys)

    for private_key_bytes in keys:
        privkey = secp256k1.PrivateKey(private_key_bytes, raw=True)
        public_key = privkey.pubkey.serialize(compressed=False)  # Uncompressed public key

        for category, address in zip(['P2PKH', 'P2SH', 'Bech32'], public_key_to_addresses(public_key)):
            address_set = address_set_partition[category]
            if address in address_set:
                print(f"[Match Found] Address: {address} (Category: {category})")
                return private_key_bytes.hex()  # Return matching private key
    return None

# Brute-force random private keys using multiprocessing
def find_matching_private_key(address_sets, total_processes=8, keys_per_process=10000):
    range_step = ORDER // total_processes
    ranges = [(i * range_step, (i + 1) * range_step - 1) for i in range(total_processes)]
    
    while True:
        for partition_index, address_set_partition in enumerate(address_sets):
            start_time = time.time()
            print(f"Searching in Partition {partition_index + 1}...")
            with multiprocessing.Pool(total_processes) as pool:
                results = pool.starmap(
                    try_private_keys_batch,
                    [(start, end, keys_per_process, address_set_partition) for start, end in ranges]
                )
                for result in results:
                    if result:
                        return result
            end_time = time.time()
            estimate_time = end_time - start_time
            # 总验证地址数
            total_verifications = keys_per_process * total_processes * (446841 + 277980 + 820108)

            # 每秒验证的地址数
            verifications_per_second = total_verifications / estimate_time
            print(f"Using {estimate_time:.3f} seconds, {verifications_per_second:.5f} addresses/seconds")

def main():
    # Load addresses into partitioned sets
    address_files = [
        "/Users/zzy/Desktop/BTC_catch/p2pkh_addresses.txt",
        "/Users/zzy/Desktop/BTC_catch/p2sh_addresses.txt",
        "/Users/zzy/Desktop/BTC_catch/bech32_addresses.txt"
    ]

    print("Loading partitioned address sets...")
    partitions = 8  # Number of partitions
    address_sets = load_address_sets(address_files, partitions=partitions)
    print(f"Address sets initialized with {partitions} partitions.")

    # Start brute-force search
    total_processes = multiprocessing.cpu_count()  # Use available CPU cores
    print(f"Using {total_processes} processes.")
    matching_key = find_matching_private_key(address_sets, total_processes=total_processes, keys_per_process=10000)
    
    if matching_key:
        print(f"[Match Found] Private Key: {matching_key}")

if __name__ == "__main__":
    main()




        
