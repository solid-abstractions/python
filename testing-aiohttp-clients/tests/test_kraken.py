# Copyright (C) 2018 Julien Hartmann
# This program is distributed under the MIT license, a copy of which you should
# have receveived along with it. If not, see <https://opensource.org/licenses/MIT>.
#
import aiohttp
import asyncio
import pytest
from decimal import Decimal
from tests.aiohttp import http_redirect, CaseControlledTestServer
from tests.certificate import ssl_certificate, TemporaryCertificate
from kraken import Kraken, PayloadError, QuotationError

TIMEOUT=1


@pytest.mark.asyncio
async def test_get_price_control(http_redirect, ssl_certificate):
    async with CaseControlledTestServer(ssl=ssl_certificate.server_context()) as server:
        http_redirect.add_server('api.kraken.com', 443, server.port)
        kraken = Kraken(session=http_redirect.session)

        task = asyncio.ensure_future(kraken.get_price('btcusd'))
        request = await server.receive_request(timeout=TIMEOUT)
        assert request.path_qs == '/0/public/Ticker?pair=XXBTZUSD'

        server.send_response(request,
            text='{"error":[],"result":{"XXBTZUSD":{"a":["3652.20000","2","2.000"]'
                 ',"b":["3651.10000","1","1.000"],"c":["3652.20000","1.00000000"],'
                 '"v":["4591.14229487","18656.76349491"],'
                 '"p":["3696.91610","3704.14127"],"t":[8602,32015],'
                 '"l":["3561.60000","3516.10000"],'
                 '"h":["3797.30000","3930.20000"],"o":"3727.50000"}}}',
            content_type='application/json'
        )
        result = await asyncio.wait_for(task, TIMEOUT)
        assert result == Decimal('3652.20000')

@pytest.mark.asyncio
async def test_get_price_invalid_pair(http_redirect, ssl_certificate):
    async with CaseControlledTestServer(ssl=ssl_certificate.server_context()) as server:
        http_redirect.add_server('api.kraken.com', 443, server.port)
        kraken = Kraken(session=http_redirect.session)

        with pytest.raises(ValueError):
            await asyncio.wait_for(kraken.get_price('foobar'), TIMEOUT)
        assert server.awaiting_request_count == 0

@pytest.mark.asyncio
async def test_get_price_connection_failure(http_redirect, unused_tcp_port):
    http_redirect.add_server('api.kraken.com', 443, unused_tcp_port)

    kraken = Kraken(session=http_redirect.session)
    with pytest.raises(QuotationError):
        await asyncio.wait_for(kraken.get_price('btcusd'), TIMEOUT)

@pytest.mark.asyncio
async def test_get_price_invalid_certificate(http_redirect):
    with TemporaryCertificate() as wrong_cert:
        async with CaseControlledTestServer(ssl=wrong_cert.server_context()) as server:
            http_redirect.add_server('api.kraken.com', 443, server.port)

            kraken = Kraken(session=http_redirect.session)
            with pytest.raises(QuotationError) as exc_info:
                await asyncio.wait_for(kraken.get_price('btcusd'), TIMEOUT)
            assert isinstance(exc_info.value.__cause__, aiohttp.ClientConnectorSSLError)
            assert server.awaiting_request_count == 0

@pytest.mark.parametrize('payload', [
    pytest.param('foobar', id='not json'),
    pytest.param('{"foo":"bar"}', id='not in kraken format'),
    pytest.param('{"error":[], "result": {}}', id='missing data'),
    pytest.param(
        '{"error":[], "result": {"XXBTZUSD":{}}}',
        id='missing price data',
    ),
    pytest.param(
        '{"error":[], "result":{"XXBTZUSD":{"a":["3652.20000","2","2.000"],'
        '"b":["3651.10000","1","1.000"],"c":["123.456.789","1.00000000"],'
        '"v":["4591.14229487","18656.76349491"],'
        '"p":["3696.91610","3704.14127"],"t":[8602,32015],'
        '"l":["3561.60000","3516.10000"],'
        '"h":["3797.30000","3930.20000"],"o":"3727.50000"}}}',
        id='invalid price',
    ),
])
@pytest.mark.asyncio
async def test_get_price_invalid_payload(http_redirect, ssl_certificate, payload):
    async with CaseControlledTestServer(ssl=ssl_certificate.server_context()) as server:
        http_redirect.add_server('api.kraken.com', 443, server.port)
        kraken = Kraken(session=http_redirect.session)

        task = asyncio.ensure_future(kraken.get_price('btcusd'))
        request = await server.receive_request(timeout=TIMEOUT)
        server.send_response(request, text=payload, content_type='application/json')
        with pytest.raises(PayloadError):
            await asyncio.wait_for(task, TIMEOUT)
