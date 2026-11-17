# Kalkulator Subnet & VLSM

Kalkulator IPv4 untuk pembelajaran jaringan: menghitung detail subnet serta membagi network induk menjadi blok VLSM berdasarkan kebutuhan host.

## Persyaratan

- Python 3.12
- `uv`
- Docker Desktop (opsional, untuk menjalankan container)

## Menjalankan aplikasi

```powershell
uv sync --dev
uv run fastapi dev main.py
```

Buka `http://127.0.0.1:8000`.

## Pengujian

```powershell
uv run pytest
```

## API

- `GET /api/subnet?ip=172.16.5.130&prefix=25` menghitung subnet IPv4.
- `POST /api/vlsm` menerima JSON `{"network":"192.168.1.0/24","kebutuhan_host":[100,50,20,2]}`.
- Input tidak valid menghasilkan HTTP 400 dengan pesan pada field `detail`.

Perhitungan `/31` mengikuti RFC 3021 dengan dua alamat host dan tanpa broadcast. Prefix `/32` mewakili satu alamat.

## Docker

Bangun image dan jalankan container:

```powershell
docker build -t subnet-calculator .
docker run -d --name subnet-app -p 8000:8000 subnet-calculator
```

Jalankan smoke test ke container lokal:

```powershell
uv run python scripts/smoke_test.py http://127.0.0.1:8000
```

Hentikan dan hapus container setelah selesai:

```powershell
docker rm -f subnet-app
```

Workflow GitHub Actions menjalankan tes unit lebih dahulu, lalu membangun image dan menjalankan smoke test container.
