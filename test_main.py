import pytest
from fastapi.testclient import TestClient

from main import alokasi_vlsm, app, hitung_subnet

client = TestClient(app)


@pytest.mark.parametrize(
    ("ip", "prefix", "expected"),
    [
        (
            "172.16.5.130",
            25,
            {
                "mask": "255.255.255.128",
                "network": "172.16.5.128",
                "broadcast": "172.16.5.255",
                "first_host": "172.16.5.129",
                "last_host": "172.16.5.254",
                "usable_hosts": 126,
            },
        ),
        (
            "10.0.0.0",
            30,
            {
                "mask": "255.255.255.252",
                "network": "10.0.0.0",
                "broadcast": "10.0.0.3",
                "first_host": "10.0.0.1",
                "last_host": "10.0.0.2",
                "usable_hosts": 2,
            },
        ),
        (
            "192.168.1.0",
            31,
            {
                "mask": "255.255.255.254",
                "network": "192.168.1.0",
                "broadcast": None,
                "first_host": "192.168.1.0",
                "last_host": "192.168.1.1",
                "usable_hosts": 2,
            },
        ),
        (
            "192.168.1.5",
            32,
            {
                "mask": "255.255.255.255",
                "network": "192.168.1.5",
                "broadcast": None,
                "first_host": "192.168.1.5",
                "last_host": "192.168.1.5",
                "usable_hosts": 1,
            },
        ),
        (
            "10.1.2.3",
            0,
            {
                "mask": "0.0.0.0",
                "network": "0.0.0.0",
                "broadcast": "255.255.255.255",
                "first_host": "0.0.0.1",
                "last_host": "255.255.255.254",
                "usable_hosts": 4294967294,
            },
        ),
    ],
)
def test_hitung_subnet(ip, prefix, expected):
    assert hitung_subnet(ip, prefix) == expected


@pytest.mark.parametrize(
    ("ip", "prefix"),
    [
        ("256.1.1.1", 24),
        ("192.168.01.1", 24),
        ("192.168.1", 24),
        ("abc", 24),
        ("", 24),
        (" 192.168.1.1", 24),
        ("192.168.1.1 ", 24),
        ("192.168.1.1", -1),
        ("192.168.1.1", 33),
        ("192.168.1.1", 24.0),
        ("192.168.1.1", True),
    ],
)
def test_hitung_subnet_menolak_input_tidak_valid(ip, prefix):
    with pytest.raises(ValueError):
        hitung_subnet(ip, prefix)


def test_get_subnet_mengembalikan_hasil_json():
    response = client.get("/api/subnet", params={"ip": "172.16.5.130", "prefix": 25})

    assert response.status_code == 200
    assert response.json()["network"] == "172.16.5.128"
    assert response.json()["broadcast"] == "172.16.5.255"
    assert response.json()["usable_hosts"] == 126


@pytest.mark.parametrize(
    ("ip", "prefix"),
    [("256.1.1.1", 24), ("192.168.01.1", 24), ("192.168.1.1", 33)],
)
def test_get_subnet_mengembalikan_400_untuk_input_tidak_valid(ip, prefix):
    response = client.get("/api/subnet", params={"ip": ip, "prefix": prefix})

    assert response.status_code == 400
    assert "detail" in response.json()


def test_get_root_mengembalikan_halaman_html():
    response = client.get("/")

    assert response.status_code == 200
    assert "<html" in response.text.lower()


def test_alokasi_vlsm_mengurutkan_dan_mengalokasikan_dari_network():
    hasil = alokasi_vlsm("192.168.1.0/24", [20, 100, 2, 50])

    assert [blok["network_cidr"] for blok in hasil] == [
        "192.168.1.0/25",
        "192.168.1.128/26",
        "192.168.1.192/27",
        "192.168.1.224/30",
    ]
    assert [blok["kebutuhan"] for blok in hasil] == [100, 50, 20, 2]
    assert hasil[0]["usable_hosts"] == 126


@pytest.mark.parametrize(
    ("network", "kebutuhan_host"),
    [
        ("192.168.1.1/24", [10]),
        ("192.168.01.0/24", [10]),
        ("192.168.1.0/33", [10]),
        ("192.168.1.0/24", []),
        ("192.168.1.0/24", [0]),
        ("192.168.1.0/24", [-1]),
        ("192.168.1.0/24", [True]),
        ("192.168.1.0/24", [200, 100]),
    ],
)
def test_alokasi_vlsm_menolak_network_atau_kebutuhan_tidak_valid(network, kebutuhan_host):
    with pytest.raises(ValueError):
        alokasi_vlsm(network, kebutuhan_host)


def test_post_vlsm_mengembalikan_hasil_json():
    response = client.post(
        "/api/vlsm",
        json={"network": "192.168.1.0/24", "kebutuhan_host": [100, 50, 20, 2]},
    )

    assert response.status_code == 200
    assert [blok["network_cidr"] for blok in response.json()] == [
        "192.168.1.0/25",
        "192.168.1.128/26",
        "192.168.1.192/27",
        "192.168.1.224/30",
    ]


def test_post_vlsm_mengembalikan_400_untuk_input_tidak_valid():
    response = client.post(
        "/api/vlsm",
        json={"network": "192.168.1.0/24", "kebutuhan_host": [200, 100]},
    )

    assert response.status_code == 400
    assert "detail" in response.json()
