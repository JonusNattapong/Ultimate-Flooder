# IP-HUNTER v2.1.0 | Advanced DDoS Toolkit & Security Suite

A powerful, multi-vector DDoS (Distributed Denial of Service) tool and network security suite written in Python. This tool features a modern CLI interface, real-time monitoring, and a wide array of attack vectors for security research and educational purposes.

## ⚠️ Disclaimer

**This tool is for educational purposes only!** Using this software to attack or disrupt any network or service without explicit permission is illegal and unethical. The author is not responsible for any misuse or damage caused by this tool. Always ensure you have proper authorization before testing any network security measures.

## ✨ Key Features

- **Modern CLI Interface**: Beautiful Terminal UI using the `rich` library with panels, tables, and live progress.
- **Real-time Monitoring**: Live statistics including Packets/Bytes sent, success rate, and active threads.
- **System Resource Watchdog**: Integrated monitoring of CPU and Memory usage with safety warnings.
- **Identity Protection**: Built-in Tor integration for anonymous HTTP attacks.
- **Advanced Stealth Mode**: Randomized headers, timing delays, and anti-forensic cleanup for maximum traceless operation.
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

## 🔒 Identity Protection & Stealth Features

IP-HUNTER includes comprehensive identity protection and advanced stealth features to help maintain anonymity and avoid detection during security testing:

### Tor Integration (Auto-Start)
- **Automatic Tor Detection**: Tool automatically detects if Tor is running
- **Auto-Start Tor**: Automatically starts Tor service if not running (when enabled)
- **SOCKS5 Proxy Support**: Uses `socks5://127.0.0.1:9050` by default
- **CLI Integration**: Simple yes/no prompt during attack configuration

### VPN Integration
- **VPN Detection**: Automatically detects active VPN connections
- **IP Verification**: Shows current public IP when VPN is active
- **Supported Providers**: NordVPN, ExpressVPN, ProtonVPN, and other common VPNs
- **Layered Protection**: Use VPN + Tor for maximum anonymity

### Advanced Stealth Mode
- **Randomized Headers**: Generates unique, realistic browser fingerprints for each request
- **Timing Randomization**: Variable delays between requests to mimic human behavior
- **Anti-Forensic Cleanup**: Automatically removes temporary files and traces
- **Proxy Chain Support**: Multiple proxy layers for enhanced anonymity

### Proxy Chain Rotation
- **Chain Creation**: Automatically creates randomized proxy chains
- **Validation**: Tests proxy validity before use
- **Failover**: Continues with working proxies if some fail
- **Load Distribution**: Distributes traffic across multiple proxies
- **Noise Traffic Generation**: Optional background traffic to mask attack patterns

### Usage with Tor:
1. **Download Tor Browser** from https://www.torproject.org/download/
2. **Run IP-HUNTER** and select Layer 7 attack
3. **Select "y"** when asked "Use Tor for anonymity?"
4. **Select "y"** when asked "Enable stealth mode (advanced anti-trace)?"
5. **Tool automatically starts Tor** if not running
6. **All HTTP requests are anonymized** through Tor network with stealth features

### Usage with VPN:
1. **Connect to VPN** using your preferred provider (NordVPN, ExpressVPN, etc.)
2. **Run IP-HUNTER** and select Layer 7 attack
3. **Select "y"** when asked "Use VPN for additional protection?"
4. **Tool will verify VPN connection** and show your VPN IP
5. **Combine with Tor** for maximum protection: VPN → Tor → Target

### Usage with Proxy Chains:
1. **Prepare proxy list** in `proxy.txt` file (one proxy per line)
2. **Run IP-HUNTER** and select Layer 7 attack
3. **Load proxies** when prompted
4. **Select "y"** when asked "Enable proxy chain rotation?"
5. **Tool validates proxies** and creates randomized chains
6. **Traffic rotates** through different proxy combinations

### Maximum Anonymity Setup:
```
User → VPN (NordVPN) → Tor Network → Proxy Chain (3-5 proxies) → Target Website
```
1. Connect to VPN first
2. Run IP-HUNTER with Layer 7 attack
3. Enable all protection layers: Tor + Stealth Mode + VPN + Proxy Chains
4. Tool provides 5+ layers of anonymity protection

### Manual Tor Setup (Alternative):
- Install Tor Browser or standalone Tor
- Ensure Tor listens on port 9050
- Tool will detect and use existing Tor instance

## ⚠️ Important Security Notice

**NO ANONYMITY METHOD IS 100% FOOLPROOF!** While IP-HUNTER provides strong identity protection features, absolute anonymity cannot be guaranteed. Here are the limitations and additional security measures:

### Tor Limitations:
- **Entry/Exit Node Logs**: Tor entry nodes can see your real IP, exit nodes can see destination
- **Timing Attacks**: Correlation of timing patterns can deanonymize users
- **Malicious Nodes**: Compromised Tor nodes can monitor traffic
- **Browser Fingerprinting**: Websites can fingerprint your browser even through Tor
- **DNS Leaks**: DNS requests may bypass Tor if not configured properly

### What IP-HUNTER Protects Against:
✅ **Direct IP Exposure**: Your real IP is hidden from targets
✅ **Basic Network Monitoring**: ISP-level traffic analysis is harder
✅ **Simple Tracing**: Direct IP-to-identity correlation is prevented
✅ **Header Analysis**: Randomized headers prevent basic fingerprinting

### What IP-HUNTER Does NOT Protect Against:
❌ **Advanced Forensics**: Law enforcement with court orders can subpoena Tor records
❌ **Timing Correlation**: Sophisticated analysis of traffic patterns
❌ **Physical Security**: Keyloggers, cameras, or compromised devices
❌ **Social Engineering**: Human error or coercion
❌ **Legal Consequences**: Using this tool illegally will still result in prosecution

### Additional Security Recommendations:

#### 1. **Use in Combination** (Defense in Depth):
```bash
# Use Tor + VPN together for better protection
VPN → Tor → Target
```
- Connect to VPN first, then use Tor through VPN
- Or use Tor over VPN for different protection layers

#### 2. **System Hardening**:
- Use Tails OS (amnesic live system)
- Disable JavaScript in Tor Browser
- Use NoScript extension
- Avoid logging into personal accounts
- Use encrypted DNS (DNSCrypt or DNS over HTTPS)

#### 3. **Operational Security (OPSEC)**:
- Never use real personal information
- Avoid patterns that can be correlated
- Use different Tor circuits for different targets
- Don't mix anonymous and non-anonymous activities
- Use bridges if Tor is blocked in your region

#### 4. **Legal Awareness**:
- **This tool is for EDUCATIONAL PURPOSES ONLY**
- Unauthorized network attacks are illegal worldwide
- Even with anonymity tools, intent and actions can be prosecuted
- Always obtain explicit written permission before testing

### Best Practice Workflow:
1. **Research Target**: Ensure you have legal authorization
2. **Setup Anonymity**: VPN → Tor → IP-HUNTER
3. **Test Safely**: Use controlled environments
4. **Clean Up**: Clear logs, restart systems
5. **Document Everything**: Keep records of authorization

**Remember: The best anonymity comes from not needing it in the first place. Always act ethically and legally.**