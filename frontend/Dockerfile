# Stage 1: Build the React application
FROM node:18-alpine AS build

WORKDIR /app

# Salin package.json dan package-lock.json (atau yarn.lock)
COPY package.json ./
COPY package-lock.json ./
# Jika menggunakan yarn, ganti dengan:
# COPY yarn.lock ./

# Instal dependensi
RUN npm install
# Jika menggunakan yarn, ganti dengan:
# RUN yarn install

# Salin sisa kode aplikasi
COPY . ./

# Bangun aplikasi untuk produksi
RUN npm run build
# Jika menggunakan yarn, ganti dengan:
# RUN yarn build

# Stage 2: Serve the application using a lightweight server (e.g., Nginx)
FROM nginx:1.25-alpine

# Salin build output dari stage sebelumnya
COPY --from=build /app/build /usr/share/nginx/html

# Salin konfigurasi Nginx kustom jika ada (opsional)
# COPY nginx.conf /etc/nginx/conf.d/default.conf

# Ekspos port yang digunakan Nginx
EXPOSE 80

# Perintah default untuk menjalankan Nginx
CMD ["nginx", "-g", "daemon off;"]
