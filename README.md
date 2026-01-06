# IP-HUNTER v2.1.0 | Advanced DDoS Toolkit & Security Suite

A powerful, multi-vector DDoS (Distributed Denial of Service) tool and network security suite written in Python. This tool features a modern CLI interface, real-time monitoring, and a wide array of attack vectors for security research and educational purposes.

## ⚠️ Disclaimer

**This tool is for educational purposes only!** Using this software to attack or disrupt any network or service without explicit permission is illegal and unethical. The author is not responsible for any misuse or damage caused by this tool. Always ensure you have proper authorization before testing any network security measures.

## ✨ Key Features

- **Modern CLI Interface**: Beautiful Terminal UI using the `rich` library with panels, tables, and live progress.
- **Real-time Monitoring**: Live statistics including Packets/Bytes sent, success rate, and active threads.
- **System Resource Watchdog**: Integrated monitoring of CPU and Memory usage with safety warnings.
- **Identity Protection**: Built-in Tor integration for anonymous HTTP attacks.
- **Layer 7 HTTP Floods**: Multiple methods including Basic, Asynchronous (aiohttp), and Cloudflare bypass.
- **Layer 4 Protocol Floods**: SYN and UDP flooding with IP spoofing capabilities.
- **Amplification Benchmarking**: Test NTP, Memcached, SSDP, and DNS amplification vectors.
- **Application Exploits**: HTTP/2 Rapid Reset, Apache/Nginx Range Header DoS.
- **Advanced Tools**: Built-in Botnet C2 Server and a multi-threaded Port Scanner with service identification.
- **Extensive Service Mapping**: Identifies over 50+ common services during port scanning (Web, DB, Games, etc.).

## 🚀 Attack Vectors

1. **Layer 7 HTTP Flood (Basic)**: Standard GET/POST flooding.
2. **Layer 7 Async HTTP Flood**: High-performance async requests with proxy support.
3. **Layer 4 SYN Flood**: TCP protocol-level flooding (requires root).
4. **Layer 4 UDP Flood**: High-velocity UDP packet bombardment (requires root).
5. **Slowloris Attack**: Low-bandwidth connection exhaustion.
6. **NTP Amplification**: Protocol-specific reflection (requires root).
7. **Botnet C2 Server**: Command and Control for managing distributed bots.
8. **Cloudflare Bypass**: Specialized headers/logic to circumvent WAFs.
9. **Memcached Amplification**: High-factor UDP reflection (requires root).
10. **SSDP Amplification**: UPnP discovery protocol reflection (requires root).
11. **DNS Amplification**: Open resolver reflection (requires root).
12. **RUDY (R U Dead Yet?)**: Slow POST data submission.
13. **HOIC Mode**: Randomized multi-vector headers and methods.
14. **HTTP/2 Rapid Reset**: Modern protocol exploit (CVE-2023-44487).
15. **Apache Killer**: Specialized Range header exhaustion.
16. **Nginx Range DoS**: Overlapping range exploitation.
17. **Port Scanner**: Professional-grade multi-threaded security auditor.

## 🛠️ Requirements

- **Python 3.8+**
- **Root/Administrator Privileges** (Required for Layer 4 & Amplification attacks)
- **Tor** (Optional, for identity protection in HTTP attacks)
- **Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
  *(Packages: requests, aiohttp, scapy, psutil, rich, PySocks)*

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/JonusNattapong/IP-HUNTER.git
cd IP-HUNTER

# Install required packages
pip install -r requirements.txt

# Optional: Install Tor for identity protection
# Download from: https://www.torproject.org/download/
# Run Tor Browser or tor service on default port 9050
```

## 🎮 Usage

You can launch the tool using the following methods:

**Windows:**
```powershell
.\run.bat
```

**Linux/Mac:**
```bash
python3 main.py
```

## 🔒 Identity Protection

IP-HUNTER includes built-in identity protection features to help maintain anonymity during security testing:

### Tor Integration (Auto-Start)
- **Automatic Tor Detection**: Tool automatically detects if Tor is running
- **Auto-Start Tor**: Automatically starts Tor service if not running (when enabled)
- **SOCKS5 Proxy Support**: Uses `socks5://127.0.0.1:9050` by default
- **CLI Integration**: Simple yes/no prompt during attack configuration

### Usage with Tor:
1. **Download Tor Browser** from https://www.torproject.org/download/
2. **Run IP-HUNTER** and select Layer 7 attack
3. **Select "y"** when asked "Use Tor for anonymity?"
4. **Tool automatically starts Tor** if not running
5. **All HTTP requests are anonymized** through Tor network

### Manual Tor Setup (Alternative):
- Install Tor Browser or standalone Tor
- Ensure Tor listens on port 9050
- Tool will detect and use existing Tor instance

### Additional Protection Features:
- **Randomized Headers**: Dynamic User-Agent and Referer rotation
- **IP Spoofing**: Built-in spoofing for Layer 4 attacks
- **Proxy Support**: Compatible with custom proxy lists
- **No Logging**: Tool doesn't store sensitive connection data