# Catatan Desain UI

## Arah Visual

Antarmuka praktikum yang ringkas dan mudah dipindai. Latar berkisi halus mengacu pada diagram jaringan; aksen hijau menandai tindakan utama dan biru menyorot hasil penting. Tipografi DM Sans dipasangkan dengan DM Mono untuk alamat dan angka.

## Struktur

- Satu halaman dengan tab Subnet dan VLSM.
- Formulir ditempatkan sebelum hasil agar alur input-ke-hasil jelas.
- Hasil subnet berupa daftar nilai; hasil VLSM berupa tabel yang dapat digulir horizontal pada layar kecil.
- Pesan kesalahan memakai kontras tinggi dan diletakkan dekat formulir.

## Responsif dan Aksesibilitas

- Formulir dan hasil menyesuaikan layar kecil.
- Tab mendukung tombol panah kiri/kanan dan atribut ARIA.
- Field memiliki label; hasil dan kesalahan diumumkan melalui live region.
- Pengurangan gerak mengikuti preferensi sistem.
