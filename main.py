#!/usr/bin/env python3  # ระบุให้ใช้ Python 3 ในการรันโปรแกรม

# IP-HUNTER-SIGNATURE-NT-191q275zj684-riridori
import sys
import argparse
sys.setrecursionlimit(2000)  # Increase recursion limit to prevent errors
from src.config import BANNER  # นำเข้าแบนเนอร์ ASCII จากโมดูล config
from src.modern_cli import ModernCLI  # นำเข้าคลาส ModernCLI จากโมดูล modern_cli

# ฟังก์ชันหลักของโปรแกรม
def main():
    """Main function - now uses modern CLI"""
    parser = argparse.ArgumentParser(description="IP-HUNTER v2.1.0-ai - Advanced DDoS Toolkit & AI-Powered Security Suite")
    parser.add_argument('--version', '-v', action='version', version='IP-HUNTER v2.1.0-ai')

    args = parser.parse_args()

    # If no arguments or after parsing, run the CLI
    ModernCLI.run()  # เรียกใช้ CLI สมัยใหม่

if __name__ == "__main__":  # ตรวจสอบว่าฟังก์ชันนี้ถูกเรียกโดยตรงหรือไม่
    main()  # เรียกใช้ฟังก์ชันหลัก