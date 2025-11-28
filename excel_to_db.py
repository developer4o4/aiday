import os
import django
import pandas as pd

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from main.models import User, Qrcode
from datetime import datetime

df = pd.read_excel("users.xlsx")

# --- 1-BOSQICH: Qrcode va User yaratish ---
user_map = {}     # Excel ID -> User object
used_qrcodes = set()  # QR lar takrorlanmasligi uchun

# Sodda funksiya: familiya yoki ism asosida gender aniqlash
def detect_gender(name: str, last_name: str) -> str:
    """
    Oddiy qoidalar asosida gender aniqlash.
    Agar familiya - 'ova', 'eva', 'qizi', 'xonova' bilan tugasa → ayol
    Aks holda → erkak
    """
    name = str(name).lower()
    last_name = str(last_name).lower()

    female_indicators = ['ova', 'eva', 'qizi', 'xonova']

    for indicator in female_indicators:
        if last_name.endswith(indicator):
            return "female"
    
    return "male"

for _, row in df.iterrows():
    excel_qr = str(row["QR Code"]).strip()

    # --- Agar QR birinchi marta uchrasa ---
    if excel_qr not in used_qrcodes:

        qr_obj, _ = Qrcode.objects.get_or_create(
            code=excel_qr,
            defaults={"is_used": True}
        )
        used_qrcodes.add(excel_qr)

    else:
        # --- QR code takrorlandi → yangi QR yaratamiz ---
        new_qr_code = Qrcode.generate_code()
        qr_obj = Qrcode.objects.create(
            code=new_qr_code,
            is_used=True
        )
        print(f"‼️ Takrorlangan QR: {excel_qr} → Yangi QR berildi: {new_qr_code}")

    # Tug'ilgan sana
    try:
        birth = pd.to_datetime(row["Tug'ilgan sana"]).date()
    except:
        birth = None

    # Gender aniqlash
    gender_value = detect_gender(row["Ism"], row["Familiya"])

    # User yaratish
    user = User.objects.create(
        qr_code=qr_obj,
        first_name=row["Ism"],
        last_name=row["Familiya"],
        middle_name=row["Sharif"],
        phone_number=str(row["Telefon"]),
        telegram_username=row["Telegram"],
        direction=row["Yo'nalish"],
        birth_date=birth,
        gender=gender_value,  # <--- gender shu yerda
        email=row["Email"],
        study_place=row["O'qish joyi"],
        region=row["Viloyat"],
        district=row["Tuman"],
        about=row["Izoh"] if pd.notna(row["Izoh"]) else "",
        is_friend=(str(row["Do'st bilan?"]).lower() == "ha"),
        is_active=True,
    )

    user_map[row["ID"]] = user

# --- 2-BOSQICH: Do‘st ulash ---
for _, row in df.iterrows():
    user = user_map[row["ID"]]

    friend_full = row["Do'st F.I.Sh"]

    if pd.isna(friend_full) or friend_full.strip() == "":
        continue

    try:
        f_first = friend_full.split()[0]
        f_last = friend_full.split()[1]

        friend_user = User.objects.get(first_name=f_first, last_name=f_last)

        user.friend = friend_user
        user.save()

    except Exception as e:
        print(f"Do‘st topilmadi: {friend_full} → {e}")

print("🎉 Tayyor! Excel malumotlari DBga muvaffaqiyatli yozildi.")
