from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse

app = FastAPI()


def _parse_ipv4(ip: str) -> int:
    if not isinstance(ip, str):
        raise ValueError("IP harus berupa alamat IPv4.")

    octets = ip.split(".")
    if len(octets) != 4:
        raise ValueError("IP harus terdiri dari tepat 4 oktet.")

    values = []
    for octet in octets:
        if not octet or any(character < "0" or character > "9" for character in octet):
            raise ValueError("Setiap oktet IP harus berupa angka desimal.")
        if len(octet) > 1 and octet.startswith("0"):
            raise ValueError("Oktet IP tidak boleh memiliki angka nol di depan.")

        value = int(octet)
        if value > 255:
            raise ValueError("Setiap oktet IP harus berada pada rentang 0-255.")
        values.append(value)

    return (values[0] << 24) | (values[1] << 16) | (values[2] << 8) | values[3]


def _format_ipv4(value: int) -> str:
    return ".".join(str((value >> shift) & 255) for shift in (24, 16, 8, 0))


def hitung_subnet(ip: str, prefix: int) -> dict:
    ip_value = _parse_ipv4(ip)
    if type(prefix) is not int or not 0 <= prefix <= 32:
        raise ValueError("Prefix harus bilangan bulat dari 0 sampai 32.")

    mask_value = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF
    network_value = ip_value & mask_value
    host_bits = 32 - prefix
    broadcast_value = network_value | ((1 << host_bits) - 1) if prefix <= 30 else None

    if prefix == 32:
        first_host_value = last_host_value = ip_value
        usable_hosts = 1
    elif prefix == 31:
        first_host_value = network_value
        last_host_value = network_value + 1
        usable_hosts = 2
    else:
        first_host_value = network_value + 1
        last_host_value = broadcast_value - 1
        usable_hosts = (1 << host_bits) - 2

    return {
        "mask": _format_ipv4(mask_value),
        "network": _format_ipv4(network_value),
        "broadcast": _format_ipv4(broadcast_value) if broadcast_value is not None else None,
        "first_host": _format_ipv4(first_host_value),
        "last_host": _format_ipv4(last_host_value),
        "usable_hosts": usable_hosts,
    }


@app.get("/api/subnet")
def api_subnet(ip: str | None = None, prefix: str | None = None) -> dict:
    try:
        if prefix is None:
            raise ValueError("Prefix wajib diisi.")
        parsed_prefix = int(prefix)
        return hitung_subnet(ip, parsed_prefix)
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@app.get("/")
def halaman_utama() -> FileResponse:
    return FileResponse(Path(__file__).with_name("index.html"))


def alokasi_vlsm(network_cidr: str, kebutuhan_host: list[int]) -> list[dict]:
    if not isinstance(network_cidr, str) or network_cidr.count("/") != 1:
        raise ValueError("Network harus berupa CIDR IPv4 yang valid.")

    ip, prefix_text = network_cidr.split("/")
    if not prefix_text or any(character < "0" or character > "9" for character in prefix_text):
        raise ValueError("Prefix network harus bilangan bulat dari 0 sampai 32.")
    if len(prefix_text) > 1 and prefix_text.startswith("0"):
        raise ValueError("Prefix network tidak boleh memiliki angka nol di depan.")

    prefix = int(prefix_text)
    subnet = hitung_subnet(ip, prefix)
    if subnet["network"] != ip:
        raise ValueError("Network CIDR harus menggunakan alamat network.")

    if not isinstance(kebutuhan_host, list) or not kebutuhan_host:
        raise ValueError("Daftar kebutuhan host tidak boleh kosong.")
    if any(type(need) is not int or need < 1 for need in kebutuhan_host):
        raise ValueError("Setiap kebutuhan host harus bilangan bulat minimal 1.")

    parent_start = _parse_ipv4(ip)
    parent_end = parent_start + (1 << (32 - prefix))
    next_address = parent_start
    allocations = []

    for need in sorted(kebutuhan_host, reverse=True):
        block_size = max(4, 1 << (need + 2 - 1).bit_length())
        next_address = (next_address + block_size - 1) & ~(block_size - 1)
        if next_address + block_size > parent_end:
            raise ValueError("Blok network tidak cukup menampung seluruh kebutuhan host.")

        block_prefix = 32 - (block_size.bit_length() - 1)
        block_ip = _format_ipv4(next_address)
        allocations.append(
            {
                "kebutuhan": need,
                "network_cidr": f"{block_ip}/{block_prefix}",
                **hitung_subnet(block_ip, block_prefix),
            }
        )
        next_address += block_size

    return allocations


@app.post("/api/vlsm")
async def api_vlsm(request: Request) -> list[dict]:
    try:
        payload = await request.json()
        if not isinstance(payload, dict):
            raise ValueError("Body harus berupa objek JSON.")
        return alokasi_vlsm(payload.get("network"), payload.get("kebutuhan_host"))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
