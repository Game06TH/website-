# config.py

import os 

# ดึงค่าการเชื่อมต่อ Render PostgreSQL จาก Environment Variables
# **สำคัญ:** ต้องตั้งค่าตัวแปรเหล่านี้ใน Render Dashboard ของ Web Service
# โค้ดนี้จะใช้ค่าจาก Environment Variables ใน Render, และใช้ค่า Localhost 
# เป็นค่าเริ่มต้น (Default) เมื่อรันบนเครื่องของคุณเอง 
# (ยกเว้น HOST, USER, PASSWORD, DATABASE ที่ต้องใช้ค่าจริงของ Render)

db_config = {
    # HOST ภายในของ Render PostgreSQL
    # ใช้ค่าจริงจาก Render เป็น Default (สำหรับทดสอบในเครื่อง) หรือดึงจาก Env Var ใน Render
    'host': os.environ.get('DB_HOST', 'dpg-d4clivf5r7bs73ag5trg-a'), # ใช้ Hostname ภายในจาก Render
    
    # ชื่อผู้ใช้ (User)
    'user': os.environ.get('DB_USER', 'freedb_game1'), # ใช้ Username จาก Render
    
    # รหัสผ่าน
    'password': os.environ.get('DB_PASSWORD', 'nChpySPjY547GpNSkq4g4HmQfsv718aC'), # ใช้รหัสผ่านจริงจาก Render
    
    # ชื่อฐานข้อมูล (Database Name)
    'database': os.environ.get('DB_NAME', 'freedb_gameth_hzr1'), # ใช้ Database Name จาก Render
    
    # Port มาตรฐานของ PostgreSQL
    'port': os.environ.get('DB_PORT', 5432) # Port มาตรฐาน 5432
}