# Ultimate Flooder

A powerful and advanced DDoS (Distributed Denial of Service) tool written in Python, designed for educational and research purposes only.

## ⚠️ Disclaimer

**This tool is for educational purposes only!** Using this software to attack or disrupt any network or service without explicit permission is illegal and unethical. The author is not responsible for any misuse or damage caused by this tool. Always ensure you have proper authorization before testing any network security measures.

## Features

- **Layer 7 HTTP Flood**: Basic HTTP GET flooding with optional proxy support
- **Layer 7 Async HTTP Flood**: Advanced asynchronous HTTP flooding with high concurrency and proxy rotation
- **Layer 7 Slowloris Attack**: Low-bandwidth attack that keeps many connections open by sending partial HTTP headers slowly
- **NTP Amplification Attack**: Reflection attack using NTP servers to amplify traffic (requires root)
- **Memcached Amplification Attack**: High-amplification reflection attack using vulnerable Memcached servers (requires root)
- **SSDP Amplification Attack**: UPnP reflection attack using SSDP multicast for traffic amplification (requires root)
- **DNS Amplification Attack**: DNS reflection attack using open DNS resolvers for massive amplification (requires root)
- **RUDY (R U Dead Yet?) Attack**: Slow POST attack that sends data byte-by-byte to exhaust server resources
- **HOIC (High Orbit Ion Cannon) Attack**: Multi-vector HTTP attack mixing GET, POST, and HEAD requests with bot-like behavior
- **HTTP/2 Rapid Reset (CVE-2023-44487)**: Exploits HTTP/2 protocol vulnerability for rapid stream resets
- **Apache Range Header DoS**: Exploits Apache's Range header processing for denial of service
- **Nginx Range Header DoS**: Exploits Nginx's Range header processing with overlapping ranges
- **Botnet C2 Server**: Command and control server for managing botnet clients
- **Cloudflare Bypass Flood**: Advanced HTTP flooding with techniques to bypass Cloudflare protection
- **Layer 4 SYN Flood**: TCP SYN packet flooding with IP spoofing (requires root)
- **Layer 4 UDP Flood**: UDP packet flooding with random data (requires root)
- Multi-threaded attacks for maximum impact
- Proxy support for HTTP attacks
- Customizable threads, duration, and target ports
- Beautiful ASCII art banner
- Modular architecture for easy extension

## Requirements

- Python 3.6+
- Root privileges (for Layer 4 attacks)
- Required Python packages:
  - requests
  - aiohttp
  - scapy

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JonusNattapong/Ultimate-Flooder.git
cd Ultimate-Flooder
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Or install as a package:
```bash
pip install -e .
```

## Usage

### Command Line Interface

After installation, you can run Ultimate Flooder from anywhere:

```bash
ultimate-flooder
```

### Direct Python Execution

Run the script directly with Python:

```bash
python main.py
```

### Shell Scripts

Use the provided shell scripts for convenience:

**Windows:**
```cmd
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

The codebase is organized into modular components for better maintainability:

```
Ultimate-Flooder/
├── main.py                    # Main entry point and menu system
├── run.py                     # CLI launcher script
├── run.bat                    # Windows batch launcher
├── run.sh                     # Unix shell launcher
├── README.md                  # Documentation
├── requirements.txt           # Python dependencies
├── setup.py                   # Package setup script
├── src/                       # Source code directory
│   ├── __init__.py           # Python package initialization
│   ├── __main__.py           # Module entry point
│   ├── ultimate_flooder/     # CLI package
│   │   ├── __init__.py       # CLI package init
│   │   └── cli.py            # Command line interface
│   ├── config.py             # Configuration constants and settings
│   ├── utils.py              # Utility functions (headers, file loading, root check)
│   ├── attacks.py            # All DDoS attack implementations
│   └── classes.py            # Menu, AttackDispatcher, and BotnetC2 classes
├── ntp_servers.txt           # NTP server list for amplification attacks
├── memcached_servers.txt     # Memcached server list for amplification
├── ssdp_servers.txt          # SSDP server list for amplification
├── dns_servers.txt           # DNS server list for amplification
└── proxy.txt                 # Proxy list (optional)
```

### Modules Overview

- **`config.py`**: Contains all configuration constants, user agents, referers, and the ASCII banner
- **`utils.py`**: Utility functions for generating headers, loading files, and checking privileges
- **`attacks.py`**: All attack functions (HTTP floods, SYN/UDP floods, Slowloris, NTP amplification, etc.)
- **`classes.py`**: Menu system, attack dispatcher, and botnet C2 server implementation
- **`main.py`**: Entry point that imports all modules and runs the interactive menu

## Usage

Run the script with Python:

```bash
python main.py
```

Follow the interactive menu to select attack type and configure parameters:

1. **Layer 7 HTTP Flood (Basic)**: Simple HTTP GET requests
2. **Layer 7 Async HTTP Flood (Advanced)**: High-performance async requests with proxies
3. **Layer 7 Slowloris Attack**: Low-bandwidth attack keeping connections open with partial headers
4. **Layer 4 SYN Flood**: Requires root privileges, spoofs source IP
5. **Layer 4 UDP Flood**: Requires root privileges, sends random UDP packets
6. **NTP Amplification Attack**: Requires root privileges, uses NTP servers for reflection/amplification
7. **Botnet C2 Server**: Starts a command and control server for botnet management
8. **Cloudflare Bypass Flood**: Advanced HTTP flooding with Cloudflare bypass techniques
9. **Memcached Amplification Attack**: High-amplification attack using vulnerable Memcached servers
10. **SSDP Amplification Attack**: UPnP reflection attack using SSDP multicast
11. **DNS Amplification Attack**: DNS reflection attack using open DNS resolvers
12. **RUDY (R U Dead Yet?) Attack**: Slow POST attack sending data byte-by-byte
13. **HOIC (High Orbit Ion Cannon) Attack**: Multi-vector attack mixing HTTP methods
14. **HTTP/2 Rapid Reset (CVE-2023-44487)**: Exploits HTTP/2 protocol vulnerability
15. **Apache Range Header DoS**: Exploits Apache Range header processing
16. **Nginx Range Header DoS**: Exploits Nginx Range header with overlapping ranges

### Parameters

- **Target**: IP address or URL
- **Port**: Target port (default: 80 for HTTP, 443 for HTTPS)
- **Threads**: Number of concurrent threads (default: 500)
- **Duration**: Attack duration in seconds (default: 60)
- **Proxy file**: Optional file containing proxy list (one per line)

### NTP Servers File

For NTP amplification, create an `ntp_servers.txt` file with vulnerable NTP servers (one per line):

```
time.nist.gov
pool.ntp.org
time.windows.com
```

### Amplification Servers Files

For maximum effectiveness with amplification attacks, create the following server files:

**memcached_servers.txt** (for Memcached amplification):
```
8.8.8.8:11211
1.1.1.1:11211
208.67.222.222:11211
```

**ssdp_servers.txt** (for SSDP amplification):
```
239.255.255.250:1900
```

**dns_servers.txt** (for DNS amplification):
```
8.8.8.8
1.1.1.1
208.67.222.222
8.8.4.4
```

### Amplification Attack Notes

- **Memcached**: ~10,000x-50,000x amplification factor, targets UDP port 11211
- **SSDP**: ~30x amplification factor, uses UPnP multicast discovery
- **DNS**: ~50x-100x amplification factor, uses ANY queries on large domains
- **Requirements**: Root privileges needed for raw socket operations

### Botnet Usage

The Botnet C2 server listens for connections from bot clients. Bots should connect and send commands like:
- `PING` - Bot heartbeat
- `RESULT:<data>` - Send results back to C2

### Cloudflare Bypass

The Cloudflare bypass flood uses various techniques:
- Rotating user agents and headers
- Random request delays
- Mixed HTTP methods (GET, POST, HEAD)
- Proxy rotation for IP diversity

## Important Notes

- **Layer 4 attacks (SYN/UDP Flood) require root/administrator privileges**
- **NTP Amplification requires root privileges for IP spoofing**
- Use at your own risk
- This tool is for educational purposes to understand DDoS attack vectors and network security
- Always test in controlled environments with permission

## License

This project is for educational purposes only. No license is provided for malicious use.
