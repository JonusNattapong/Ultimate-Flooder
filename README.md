# IP-HUNTER v2.1.0-ai | Advanced DDoS Toolkit & AI-Powered Security Suite

**© 2026 Nattapong Tapachoom. สิทธิในทรัพย์สินทางปัญญาและลิขสิทธิ์ทั้งหมดเป็นของ ณัฐพงศ์ ตะปะชุม**
**[PROPRIETARY SOFTWARE - RESTRICTED DISTRIBUTION]**

**🚀 AI Integration Release: Offensive Red Team Training & Strategy Generation**

---

### 🏛️ ประกาศทางกฎหมายและข้อตกลงการใช้งาน (Strict Legal Notice)

**ซอฟต์แวร์นี้เป็นทรัพย์สินทางปัญญาของ ณัฐพงศ์ ตะปะชุม (Nattapong Tapachoom)** 
ห้ามมิให้มีการเผยแพร่ ดัดแปลง ทำซ้ำ หรือแจกจ่ายส่วนใดส่วนหนึ่งของซอฟต์แวร์นี้ โดยไม่ได้รับอนุญาตเป็นลายลักษณ์อักษรจากเจ้าของลิขสิทธิ์โดยตรง

#### 1. การจำกัดความรับผิดชอบ (No Liability Claim)
ผู้พัฒนา **"จะไม่รับผิดชอบใดๆ ทั้งสิ้น"** ต่อเหตุการณ์ ความเสียหาย หรือผลกระทบทางกฎหมายที่เกิดขึ้นจากการนำซอฟต์แวร์นี้ไปใช้งานในทุกรูปแบบ ผู้ใช้เป็นผู้แบกรับความเสี่ยงและผลทางกฎหมายแต่เพียงผู้เดียว

#### 2. การดำเนินคดีทางกฎหมาย (Prosecution Warning)
หากพบเห็นการนำรหัสต้นฉบับ (Source Code) หรือไฟล์โปรแกรมไปดัดแปลงเพื่อจำหน่าย แจกจ่ายฟรี หรือนำไปใช้ในทางที่สร้างความเสื่อมเสีย **ผู้พัฒนาจะดำเนินคดีตามกฎหมายสูงสุดให้ถึงที่สุด (Maximum Prosecution)** ทั้งทางแพ่งและทางอาญา โดยไม่มีการเจรจาหรือยอมความใดๆ ทั้งสิ้น

---

A powerful, multi-vector DDoS (Distributed Denial of Service) tool and network security suite written in Python. This tool features a modern CLI interface, real-time monitoring, and a wide array of attack vectors for security research and educational purposes.

## 🚀 Quick Start Guide

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/JonusNattapong/IP-HUNTER.git
   cd IP-HUNTER
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the tool**:
   ```bash
   python main.py
   ```

### Basic Usage

1. **Select an attack** from the menu by entering the corresponding ID (e.g., `1` for HTTP Flood).
2. **Enter target details**:
   - Target: IP address or URL (e.g., `http://example.com` or `192.168.1.1`)
   - Port: Default ports are used if not specified
   - Threads: Number of concurrent threads (default: 100, max: 1000)
   - Duration: Attack duration in seconds (default: 60, max: 3600)
3. **Configure options** (optional):
   - Proxies: Provide a file path to a list of proxies
   - Stealth Mode: Enable randomized headers and delays
   - Tor Integration: Route traffic through Tor for anonymity
4. **Monitor progress**: Real-time statistics are displayed during execution.

### Configuration

- **Proxy File**: Create a `proxies.txt` file with one proxy per line (format: `ip:port` or `user:pass@ip:port`).
- **Environment Variables**: Set `TOR_ENABLED=1` to force Tor usage.
- **Advanced Settings**: Edit `src/config.py` for default values like thread limits and timeouts.

### Examples

- **HTTP Flood**: Select ID `1`, target `http://target.com`, threads `50`, duration `30`.
- **Port Scan**: Select ID `17`, target `192.168.1.1`, ports `1-65535`.
- **Vulnerability Scan**: Select ID `23`, target `http://target.com`.

**Note**: Always test in controlled environments. Unauthorized use is illegal.

## ⚠️ Disclaimer

**This tool is for educational purposes only!** Using this software to attack or disrupt any network or service without explicit permission is illegal and unethical. The author is not responsible for any misuse or damage caused by this tool. Always ensure you have proper authorization before testing any network security measures.

## ✨ Key Features

- **🤖 AI-Powered Offensive Intelligence**: Integrated AI assistant using fine-tuned models on red team datasets for attack strategy generation.
- **🧠 Smart Threat Intelligence**: AI-enhanced threat reports with context-aware attack recommendations and risk analysis.
- **🎯 Adaptive Attack Strategies**: AI analyzes target information and suggests optimal attack vectors based on service type and vulnerabilities.
- **📊 AI Training Pipeline**: Complete training infrastructure using Hugging Face datasets (WNT3D/Ultimate-Offensive-Red-Team).
- **🔄 Fallback AI Mode**: Works offline with pre-defined offensive techniques when full AI models aren't available.
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

### Application Layer (Layer 7)
1. **HTTP Flood (Basic)**: Standard GET/POST flooding for web services.
2. **Async HTTP Flood**: High-performance async requests with proxy support.
5. **Slowloris Attack**: Low-bandwidth connection exhaustion using partial headers.
8. **Cloudflare Bypass**: Specialized logic to circumvent WAF and CDN protection.
12. **RUDY (R U Dead Yet?)**: Slow POST data submission to tie up threads.
13. **HOIC Mode**: High Orbit Ion Cannon style multi-vector headers/methods.
14. **HTTP/2 Rapid Reset**: Exploits stream cancellation in HTTP/2 (CVE-2023-44487).
15. **Apache Killer**: Range header exhaustion targeting Apache servers.
16. **Nginx Range DoS**: Overlapping range exploitation for Nginx.
22. **AI-Adaptive Flood**: Smart flood that adjusts intensity based on server latency with AI-enhanced targeting.
33. **Mixed Vector Flood**: Randomized combination of L7 techniques in a single attack.
34. **Slow Post Attack**: Advanced variant of RUDY with randomized drip-feeding.

### Network Layer (Layer 4)
3. **SYN Flood**: TCP protocol-level flooding with IP spoofing (requires root).
4. **UDP Flood**: High-velocity UDP packet bombardment (requires root).
19. **Hybrid ICMP Attack**: Combined ICMP Flood and Ping of Death exploit.
35. **QUIC Flood**: Targets the modern HTTP/3 (QUIC) protocol.

### Amplification & Reflection
6. **NTP Amplification**: Protocol-specific reflection (requires root).
9. **Memcached Amplification**: Massive UDP amplification factor (~50,000x).
10. **SSDP Amplification**: UPnP discovery protocol reflection (requires root).
11. **DNS Amplification**: Exploiting open resolvers for traffic multiplication.

### Infrastructure & Botnet
7. **Botnet C2 Server**: Command and Control system for managing remote bots.
18. **Local Bot Client**: Connects local machine to a C2 for distributed operation.
00. **Interactive C2 Shell**: Management console for connected botnet nodes.

### OSINT & Reconnaissance
0. **Target Library**: Save and manage targets for quick-access (ID 0).
17. **Advanced Port Scanner**: Multi-threaded auditor with service identification.
20. **Network Discovery**: Comprehensive subnet scanner for active hosts.
21. **IP Intel Tracker**: Deep geolocation and ASN intelligence gathering.
25. **Domain OSINT**: Automated subdomain and DNS record harvester.
31. **CVE Explorer**: Real-time vulnerability search via NVD/NIST databases.
32. **Web Exposure Sniper**: Deep scan for leaked configs and exposed directories.

### Cyber-Sec Toolkit
 23. **Vulnerability Scout**: Quick scans for misconfigured headers (XSS, CORS, CSP) and common sensitive paths.
 24. **Brute Force Suite**: Multi-protocol credential auditor for FTP, SSH, and HTTP Basic Auth.
 26. **Proxy Auto-Pilot**: Automated scraper that gathers, validates, and benchmarks public proxies for latency.
 27. **WiFi Ghost Recon**: Nearby wireless signal monitoring and BSSID tracking (Windows netsh optimized).
 28. **Live Packet Insight**: Real-time traffic sniffer using Scapy to analyze protocol distribution (TCP/UDP/ICMP).
 29. **Payload Laboratory**: Interactive reverse shell generator for Python, Bash, Netcat, and PowerShell.
 30. **Identity Cloak**: Operational Security auditor that checks for IP leaks, VPN status, and MAC address exposure.

## 🤖 AI Integration & Offensive Intelligence

IP-HUNTER v2.1.0-ai introduces cutting-edge AI capabilities for intelligent offensive security operations:

### AI-Powered Attack Strategy Generation
- **Context-Aware Analysis**: AI analyzes target information (ports, services, vulnerabilities) to suggest optimal attack vectors
- **Target-Specific Strategies**:
  - **Web Servers**: SQL Injection, XSS, Directory Traversal, CSRF analysis
  - **Databases**: Blind SQL Injection, Union-based attacks, Data exfiltration techniques
  - **Networks**: Port scanning, MITM attacks, ARP poisoning, Wireless exploitation
  - **Unknown Targets**: Reconnaissance and vulnerability assessment approaches

### Smart Threat Intelligence Reports
- **AI-Enhanced Reports**: Threat intelligence reports now include AI-generated attack strategies alongside defensive recommendations
- **Risk-Based Analysis**: AI evaluates target risk scores and suggests appropriate offensive techniques
- **Professional Output**: Combined defensive and offensive intelligence in unified reports

### Training Infrastructure
- **Hugging Face Integration**: Uses `WNT3D/Ultimate-Offensive-Red-Team` dataset for model training
- **Fine-Tuning Pipeline**: Complete training scripts for custom model development
- **Fallback Mode**: Pre-defined offensive techniques when full AI models aren't available

### AI Features in Action
```bash
# AI automatically activates during threat intelligence gathering
# Example: Scanning a web server triggers AI analysis

Target Analysis: Apache server on ports 80,443 with MySQL backend
AI Strategy Suggestions:
1. SQL Injection testing on login forms and search parameters
2. XSS vulnerability scanning on user input fields
3. Directory traversal attacks on file upload endpoints
4. CSRF token analysis and bypass attempts
5. API endpoint enumeration and parameter tampering
```

### Training Your Own AI Model
```bash
# Train custom AI model (requires GPU recommended)
python train_ai_model.py

# Test AI integration
python test_ai_integration.py
```

### AI Integration Benefits
- **Intelligent Targeting**: No more guesswork - AI suggests the most effective attack vectors
- **Educational Value**: Learn offensive techniques through AI-guided analysis
- **Research Enhancement**: Accelerate red teaming research with AI assistance
- **Operational Efficiency**: Reduce time spent on manual attack strategy development

## 🛰️ Technical Deep-Dive

### Smart Target Library (ID 0)
The Target Library provides **persistence** for your operations. Any host discovered via the [Network Scanner](src/attacks/scanning.py) or entered manually can be "Locked" into the library. 
- Auto-saves to `txt/locked_targets.txt`
- Quick-select IDs to avoid re-typing long URLs or IPs.
- Seamlessly integrates with all 35 attack vectors.

### Adaptive IA Flooding (ID 22)
Unlike standard flooders, the **Adaptive Flood** monitors the target's response latency. 
- If the server responds quickly, it **ramps up** thread intensity.
- If it detects a `429 Too Many Requests` or `503 Service Unavailable`, it **backs off** to preserve proxy health.
- Automatically rotates User-Agents when a WAF block (403) is detected.

### Hybrid ICMP & QUIC (IDs 19, 35)
- **ID 19**: Combines a high-velocity ICMP Echo Flood with the **Ping of Death** (oversized packet fragments) to overwhelm network stacks and firewalls simultaneously.
- **ID 35**: Specifically targets the **QUIC (HTTP/3)** protocol over UDP 443, bypassing many traditional TCP-based WAF rules.

### Botnet C2 Infrastructure (IDs 7, 18, 00)
IP-HUNTER features a built-in **Command & Control** system:
1. **Server (ID 7)**: Listen for incoming bot connections on a custom port.
2. **Client (ID 18)**: Deploy a lightweight bot that connects back to your C2 center.
3. **Interactive Shell (ID 00)**: A real-time terminal to broadcast flood commands to your entire botnet with a single "attack" command.

## 🧪 Testing State (Current)
- **Status**: ✅ All 35 attack vectors verified + AI integration complete
- **AI Integration**: ✅ Offensive strategy generation and threat intelligence enhancement
- **Target**: `http://203.154.83.24/` (Functional verification completed)
- **UI Architecture**: Enhanced Cyberpunk HUD with AI-enhanced monitoring and professional reporting
- **AI Training**: ✅ Pipeline ready with WNT3D/Ultimate-Offensive-Red-Team dataset

## 🛠️ Requirements

- **Python 3.8+**
- **Root/Administrator Privileges** (Required for Layer 4 & Amplification attacks)
- **Tor** (Optional, for identity protection in HTTP attacks)
- **Configuration**: Create a `.env` file based on `.env example`
  - `MASTER_ADMIN_KEY`: Random 32-character hex key required for C2 access.
  - `OPEN_ROUTER`: API key for AI-Adaptive logic.
- **Dependencies**:
  ```bash
  pip install -r requirements.txt
  ```
  *(Core: requests, aiohttp, scapy, psutil, rich, PySocks)*
  *(AI/ML: torch, transformers, datasets, accelerate)*

## 📦 Installation

```bash
# Clone the repository
git clone https://github.com/JonusNattapong/IP-HUNTER.git
cd IP-HUNTER

# Setup environment
cp ".env example" .env
# Edit .env with your keys

# Install required packages
pip install -r requirements.txt

# Optional: Train AI model for enhanced intelligence (requires GPU recommended)
python train_ai_model.py

# Test AI integration
python test_ai_integration.py

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
## 📜 License & Copyright (ลิขสิทธิ์และข้อตกลงการใช้งาน)

**Copyright © 2026 Nattapong Tapachoom. All Rights Reserved.**

ซอฟต์แวร์นี้เป็นลิขสิทธิ์ของ **ณัฐพงศ์ ตะปะชุม** ห้ามมิให้ผู้ใดทำการคัดลอก ทำซ้ำ ดัดแปลง แก้ไข เผยแพร่ หรือแจกจ่ายส่วนหนึ่งส่วนใดหรือทั้งหมดของซอฟต์แวร์นี้โดยไม่ได้รับอนุญาตเป็นลายลักษณ์อักษรโดยเด็ดขาด

**เงื่อนไขและข้อตกลงสำคัญ (Full Proprietary Disclosure):**

1.  **Strict Non-Redistribution**: ห้ามแจกจ่ายไฟล์ต้นฉบับหรือไฟล์ที่ผ่านการคอมไพล์แล้วไปยังแพลตฟอร์มสาธารณะใดๆ หากตรวจพบข้อมูลรั่วไหลจากผู้ใช้คนใด จะมีการระงับสิทธิ์และดำเนินคดีทันที
2.  **No Liability Claim**: ผู้พัฒนาจะไม่รับผิดชอบต่อความเสียหาย การถูกระงับบัญชี หรือการถูกดำเนินคดีทางกฎหมายใดๆ ที่เกิดขึ้นจากการนำเครื่องมือนี้ไปใช้ในทางที่ผิดกฎหมาย (ผู้ใช้ต้องแบกรับความเสี่ยงเอง 100%)
3.  **Built-in Auditing**: ซอฟต์แวร์มีการใช้ระบบตรวจสอบการเข้าถึง (Telemetry) เพื่อบันทึกข้อมูลการรันโปรแกรมพื้นฐาน เพื่อป้องกันการนำโค้ดไปดัดแปลงหรือขายต่อโดยมิชอบ
4.  **Copyright Protection**: รหัสต้นฉบับ ลอจิกการโจมตี และโครงสร้างโปรแกรมทั้งหมดได้รับการคุ้มครองภายใต้ **พ.ร.บ. ลิขสิทธิ์ และ พ.ร.บ. คอมพิวเตอร์**
5.  **Maximum Prosecution**: หากมีการตรวจพบว่ามีการนำไป ดัดแปลง แจกจ่าย หรือใช้งานโดยมิได้รับอนุญาต เจ้าของลิขสิทธิ์จะ**ดำเนินคดีตามกฎหมายสูงสุดทั้งทางแพ่งและทางอาญาให้ถึงที่สุด** โดยยึดตามเขตอำนาจศาลในประเทศไทย

---

**IP-HUNTER - Advanced Defense & Recon Toolkit**
