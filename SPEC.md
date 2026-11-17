# Spesifikasi Kalkulator Subnet & VLSM

## Tujuan

Menyediakan kalkulator IPv4 berbasis web yang hasilnya dapat diperiksa untuk pembelajaran subnetting dan VLSM.

## Aturan Validasi

- Alamat IPv4 terdiri tepat dari empat oktet desimal 0-255, tanpa nol di depan dan tanpa spasi.
- Prefix subnet adalah bilangan bulat 0-32.
- Input fungsi yang tidak valid menghasilkan `ValueError`; API mengubahnya menjadi HTTP 400 dengan field `detail`.
- Network induk VLSM harus berupa CIDR IPv4 valid yang alamat IP-nya sama dengan alamat network.
- Kebutuhan host VLSM harus berupa daftar tidak kosong berisi bilangan bulat positif.
- VLSM menggunakan blok minimum /30 dan ditolak jika semua blok tidak muat.

## Kontrak Fungsi

`hitung_subnet(ip: str, prefix: int) -> dict` menghasilkan `mask`, `network`, `broadcast`, `first_host`, `last_host`, dan `usable_hosts`. Network dihitung dengan operasi bitwise AND. Prefix /0 sampai /30 memakai `2^(32-prefix) - 2` host. Prefix /31 mengikuti RFC 3021 (dua host, tanpa broadcast); /32 menghasilkan satu host dan tanpa broadcast.

`alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]` mengurutkan kebutuhan dari terbesar, menggunakan ukuran blok pangkat dua terkecil yang dapat menampung kebutuhan host ditambah dua alamat, dan mengalokasikan berurutan dari network induk. Setiap entri berisi `kebutuhan`, `network_cidr`, serta seluruh kunci hasil `hitung_subnet`.

## Kontrak API

- `GET /api/subnet?ip=&prefix=` menghitung satu subnet.
- `POST /api/vlsm` menerima JSON dengan field `network` dan `kebutuhan_host`.
- `GET /` menyajikan `index.html`.
- Kesalahan input menghasilkan HTTP 400 dengan field JSON `detail`.

## Halaman Web

Satu halaman responsif memiliki mode Subnet dan VLSM. Mode Subnet menampilkan mask, network, broadcast, host pertama/terakhir, dan jumlah host. Mode VLSM memungkinkan penambahan/penghapusan kebutuhan dan menampilkan tabel alokasi. Kesalahan ditampilkan dekat formulir.

## Tabel Test Case

| Kasus | Input | Hasil yang diharapkan |
|---|---|---|
| Subnet /25 | `172.16.5.130/25` | Network `172.16.5.128`, broadcast `172.16.5.255`, 126 host |
| Subnet /30 | `10.0.0.0/30` | Host `.1` sampai `.2`, broadcast `.3`, 2 host |
| Point-to-point | `192.168.1.0/31` | 2 host, tanpa broadcast |
| Satu alamat | `192.168.1.5/32` | 1 host, tanpa broadcast |
| IP/prefix tidak valid | `256.1.1.1/24`, `192.168.01.1/24`, alamat tidak lengkap, teks, prefix `-1` atau `33` | Ditolak |
| VLSM muat | `192.168.1.0/24`, kebutuhan `[100,50,20,2]` | `/25` `.0`, `/26` `.128`, `/27` `.192`, `/30` `.224` |
| VLSM tidak muat | `192.168.1.0/24`, kebutuhan `[200,100]` | Ditolak |

## Di Luar Cakupan

IPv6, routing, reservasi alamat, dan penyimpanan hasil perhitungan tidak termasuk.
