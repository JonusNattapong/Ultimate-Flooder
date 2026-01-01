#!/usr/bin/env python3  # ระบุให้ใช้ Python 3 ในการรันโปรแกรม

from src.config import BANNER  # นำเข้าแบนเนอร์ ASCII จากโมดูล config
from src.classes import Menu, AttackDispatcher  # นำเข้าคลาส Menu และ AttackDispatcher จากโมดูล classes

print(BANNER)  # แสดงแบนเนอร์ ASCII เมื่อโปรแกรมเริ่มทำงาน

# ฟังก์ชันหลักของโปรแกรม
def main():
    print("Ultimate Flooder v1.0 - Advanced DDoS Tool")  # แสดงชื่อและเวอร์ชันของเครื่องมือ
    print("Coded for Educational Purposes Only")  # แสดงคำเตือนว่าสำหรับการศึกษาเท่านั้น
    print("=" * 50)  # แสดงเส้นคั่นความยาว 50 ตัวอักษร

    while True:  # วนลูปไม่สิ้นสุดจนกว่าผู้ใช้จะออก
        choice = Menu.display()  # แสดงเมนูและรับค่าการเลือกจากผู้ใช้

        if choice.lower() in ['q', 'quit', 'exit']:  # ตรวจสอบว่าผู้ใช้ต้องการออกหรือไม่
            print("Goodbye!")  # แสดงข้อความลาก่อน
            break  # ออกจากลูป

        if choice not in Menu.ATTACKS:  # ตรวจสอบว่าการเลือกถูกต้องหรือไม่
            print("Invalid choice! Please select a valid option.")  # แสดงข้อความแจ้งเตือนการเลือกไม่ถูกต้อง
            continue  # วนกลับไปแสดงเมนูใหม่

        try:  # ลองทำการโจมตี
            params = Menu.get_attack_params(choice)  # รับพารามิเตอร์สำหรับการโจมตี
            AttackDispatcher.execute(choice, params)  # เรียกใช้การโจมตีตามที่เลือก
        except KeyboardInterrupt:  # จัดการกรณีที่ผู้ใช้กด Ctrl+C
            print("\nAttack interrupted by user.")  # แสดงข้อความว่าการโจมตีถูกขัดจังหวะ
        except Exception as e:  # จัดการข้อผิดพลาดอื่นๆ
            print(f"Error during attack: {e}")  # แสดงข้อผิดพลาดที่เกิดขึ้น

if __name__ == "__main__":  # ตรวจสอบว่าฟังก์ชันนี้ถูกเรียกโดยตรงหรือไม่
    main()  # เรียกใช้ฟังก์ชันหลัก