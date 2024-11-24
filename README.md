# BTC Private Key Finder  

**Disclaimer: This tool is intended solely for the recovery of private keys associated with Bitcoin addresses that you own. Using this tool to attempt to access Bitcoin addresses without authorization is illegal and strictly prohibited. By using this software, you confirm that you are complying with all applicable laws and regulations. The authors are not responsible for any misuse of this tool.**

---

## Overview  

BTC Private Key Finder is a multi-process brute-force tool designed to help users recover lost Bitcoin private keys from a list of owned Bitcoin addresses. The tool is optimized for macOS and leverages multiprocessing and the secp256k1 cryptographic library for high-speed performance.  

---

## Features  

- **Optimized for macOS**: Leverages macOS multiprocessing capabilities for efficiency.  
- **Supports Large Address Sets**: Loads Bitcoin addresses from a file and performs quick lookups using a set.  
- **High Performance**: Uses secp256k1 for cryptographic operations and multiprocessing to maximize speed.  
- **Real-Time Feedback**: Provides performance metrics, including attempts per second and time elapsed.  
- **Mainnet Address Compatibility**: Generates addresses suitable for Bitcoin’s main network.  

---

## Installation  

### Prerequisites  

- Python 3.x installed on macOS  
- `pip` (Python package manager)  

### Steps  

1. **Clone the Repository**:  
   ```bash
   git clone https://github.com/yourusername/btc-private-key-finder.git
   cd btc-private-key-finder


2. **Install Dependencies**:
   Install the necessary Python libraries with:
   ```bash
   pip install secp256k1 base58 numpy
   ```

3. **Prepare the Address File**:
   Create a text file named `pure_addresses.txt` in the project directory. Add one Bitcoin address per line, like so:
   ```
   1ExampleBitcoinAddress1
   1ExampleBitcoinAddress2
   ```

---

## Usage

### Configure the Address File Path:

Open the `main.py` file and ensure the path to the `pure_addresses.txt` file is correct:
```python
address_file = "/path/to/pure_addresses.txt"
```

### Run the Tool:

Execute the script:
```bash
python main.py
```

### Monitoring Progress:

The tool will generate random private keys and test them against the provided addresses.
Progress logs will include:
- Time elapsed.
- Number of keys tested per second.
- Alerts if a matching private key is found.

### Example Output:

If a match is found, it outputs:
```plaintext
[Matching Address Found] Address: 1ExampleBitcoinAddress
[Private Key (Hex)] e1f30b7b1f3e1a9ff1c50eac22f12ab6e82e49f1ec90c2d8ad3d4b82eb3d3b8a
```

---

## Performance

- **Full CPU Utilization**: By default, the tool uses all available CPU cores for maximum throughput.
- **Configurable Rounds**: Adjust the number of private keys tested per process in `main.py` for your hardware.
- **Real-Time Logs**: Logs key testing speed, time per round, and other performance metrics.

---


## Disclaimer

This tool is for **lawful and personal use only**. Use it solely to recover private keys for Bitcoin addresses that you legally own. Unauthorized use is illegal and may lead to severe consequences. By using this software, you accept full responsibility for your actions.

---

## License

This project is licensed under the [MIT License](LICENSE). See the LICENSE file for details.

---

## Contributing

Contributions are welcome! Follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature or fix bug"
   ```
4. Push your branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

