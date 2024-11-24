import os
import hashlib
import secp256k1  # Optimized elliptic curve library
import base58
import multiprocessing
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import time

# Define the ORDER of the SECP256k1 curve
ORDER = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141

# Load Bitcoin addresses into a set for quick lookup
def load_addresses(filename):
    with open(filename, "r") as f:
        return set(line.strip() for line in f)

# Convert a private key to a public key using secp256k1
def private_key_to_public_key(private_key_bytes):
    privkey = secp256k1.PrivateKey(private_key_bytes, raw=True)
    public_key = privkey.pubkey.serialize(compressed=False)  # Uncompressed public key
    return public_key

# Convert a public key to a Bitcoin address
def public_key_to_address(public_key):
    sha256 = hashlib.sha256(public_key).digest()
    ripemd160 = hashlib.new('ripemd160', sha256).digest()
    network_byte = b'\x00' + ripemd160  # Mainnet network byte
    checksum = hashlib.sha256(hashlib.sha256(network_byte).digest()).digest()[:4]
    address_bytes = network_byte + checksum
    address = base58.b58encode(address_bytes).decode('utf-8')
    return address

# Core brute-force logic, testing random private keys
def try_private_keys(num_keys, addresses, round_number):
    for i in range(num_keys):
        private_key_bytes = os.urandom(32)
        private_key_int = int.from_bytes(private_key_bytes, 'big')
        if 1 <= private_key_int < ORDER:
            public_key = private_key_to_public_key(private_key_bytes)
            address = public_key_to_address(public_key)
            if address in addresses:
                print(f"[Matching Address Found] Address: {address}")
                print(f"[Private Key (Hex)] {private_key_bytes.hex()}")
                return private_key_bytes.hex()
    return None

# Brute-force random private keys using multiprocessing
def find_matching_private_key(addresses, total_processes=8, keys_per_process=100000):
    round_number = 0
    while True:
        start_time = time.time()
        with ProcessPoolExecutor(max_workers=total_processes) as executor:
            futures = [executor.submit(try_private_keys, keys_per_process, addresses, round_number) for _ in range(total_processes)]
            for future in futures:
                result = future.result()
                if result:
                    print("[Match Found] A matching private key was found. Stopping all processes.")
                    print(result)
                    return result
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"Round {round_number + 1} completed. Time taken: {elapsed_time:.5f} seconds, Speed: {keys_per_process*8*len(addresses)/elapsed_time} attempts/second.")
        round_number += 1
    print("No matching private key found.")
    return None

def main():
    # Load addresses from file
    address_file = "/Your-path-to/addresses.txt"
    addresses = load_addresses(address_file)
    print(f"Loaded {len(addresses)} addresses.")

    # Start brute-force search
    total_processes = multiprocessing.cpu_count()
    print(f"Using {total_processes} processes.")
    find_matching_private_key(addresses, total_processes=total_processes, keys_per_process=100000)

if __name__ == "__main__":
    main()
