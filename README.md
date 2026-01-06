# IP-HUNTER | Advanced DDoS Toolkit & Security Suite

A powerful, multi-vector DDoS (Distributed Denial of Service) tool and network security suite written in Python. This tool features a modern CLI interface, real-time monitoring, and a wide array of attack vectors for security research and educational purposes.

## ⚠️ Disclaimer

**This tool is for educational purposes only!** Using this software to attack or disrupt any network or service without explicit permission is illegal and unethical. The author is not responsible for any misuse or damage caused by this tool. Always ensure you have proper authorization before testing any network security measures.

## ✨ Key Features

- **Modern CLI Interface**: Beautiful Terminal UI using the `rich` library with panels, tables, and live progress.
- **Real-time Monitoring**: Live statistics including Packets/Bytes sent, success rate, and active threads.
- **System Resource Watchdog**: Integrated monitoring of CPU and Memory usage with safety warnings.
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
- **Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
  *(Packages: requests, aiohttp, scapy, psutil, rich)*

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/JonusNattapong/Ultimate-Flooder.git
cd Ultimate-Flooder

# Install required packages
pip install -r requirements.txt
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