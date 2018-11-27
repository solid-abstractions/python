Unit testing aiothttp clients
=============================

This code supports article https://solidabstractions.com/2018/testing-aiohttp-client.

Using
=====

```bash
python -m venv env
. env/bin/activate
pip install -qr requirements.txt
pytest -v
```

Sample session:

```
spectras$ python3 -m venv env
spectras$ . env/bin/activate
(env) spectras$ pip install -qr requirements.txt
(env) spectras$ pytest -v
============================= test session starts ==============================
collecting ... collected 9 items

tests/test_kraken.py::test_get_price_control PASSED                      [ 11%]
tests/test_kraken.py::test_get_price_invalid_pair PASSED                 [ 22%]
tests/test_kraken.py::test_get_price_connection_failure PASSED           [ 33%]
tests/test_kraken.py::test_get_price_invalid_certificate PASSED          [ 44%]
tests/test_kraken.py::test_get_price_invalid_payload[not json] PASSED    [ 55%]
tests/test_kraken.py::test_get_price_invalid_payload[not in kraken format] PASSED [ 66%]
tests/test_kraken.py::test_get_price_invalid_payload[missing data] PASSED [ 77%]
tests/test_kraken.py::test_get_price_invalid_payload[missing price data] PASSED [ 88%]
tests/test_kraken.py::test_get_price_invalid_payload[invalid price] PASSED [100%]

=========================== 9 passed in 0.10 seconds ===========================
```
