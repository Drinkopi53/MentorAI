# Gunakan image Python resmi sebagai dasar
FROM python:3.9-slim

# Atur direktori kerja di dalam container
WORKDIR /app

# Salin file requirements.txt terlebih dahulu untuk memanfaatkan caching Docker layer
COPY requirements.txt .

# Instal dependensi
# --no-cache-dir untuk mengurangi ukuran image
# --default-timeout=100 untuk mengatasi potensi timeout saat mengunduh package besar
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# Salin direktori aplikasi kita (yang berisi main.py dan file lainnya) dan file lain di root backend (seperti requirements.txt yang sudah disalin)
COPY ./app /app/app
# Jika ada file lain di root backend yang perlu disalin selain requirements.txt dan direktori app, tambahkan di sini.
# Misalnya: COPY ./other_config.json /app/other_config.json
# Untuk saat ini, kita hanya memiliki direktori app dan requirements.txt.

# Ekspos port yang digunakan oleh FastAPI (sama dengan yang ada di uvicorn.run atau command di docker-compose)
EXPOSE 8000

# Perintah untuk menjalankan aplikasi ketika container dimulai
# Ini akan dioverride oleh command di docker-compose.yml untuk development (dengan --reload dan --root-path)
# Namun, ini adalah default yang baik untuk produksi jika tidak dioverride.
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
