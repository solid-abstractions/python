# Copyright (C) 2018 Julien Hartmann
# This program is distributed under the MIT license, a copy of which you should
# have receveived along with it. If not, see <https://opensource.org/licenses/MIT>.
#
import aiohttp
import decimal
import json

class QuotationError(Exception): pass
class PayloadError(QuotationError): pass


class Kraken:
    ROOT_URL = 'https://api.kraken.com/0/'
    TICKER_ENDPOINT = 'public/Ticker?pair={pair}'
    PAIRS = {
        'btcusd': 'XXBTZUSD',
        'ethusd': 'XETHZUSD',
        'ltcusd': 'XLTCZUSD',
        'xrpusd': 'XXRPZUSD',
    }

    def __init__(self, *, session):
        self._session = session

    async def get_price(self, pair):
        ''' Return latest trade price for given pair '''
        try:
            pair = self.PAIRS[pair]
        except KeyError:
            raise ValueError('unknown pair name %r' % pair)
        data = await self._fetch(self.TICKER_ENDPOINT.format(pair=pair))
        try:
            return decimal.Decimal(data[pair]['c'][0])
        except (KeyError, IndexError, decimal.DecimalException) as exc:
            raise PayloadError('failed to parse kraken response') from exc

    async def _fetch(self, endpoint):
        ''' Fetch data from endpoint, handling errors and returning parsed result '''
        try:
            async with self._session.get(self.ROOT_URL + endpoint) as response:
                data = await response.json()
            error = data.get('error')
            if error:
                raise QuotationError(error[0])
            return data['result']
        except aiohttp.ClientError as exc:
            raise QuotationError('failed to connect to kraken api') from exc
        except (json.JSONDecodeError, KeyError, IndexError) as exc:
            raise PayloadError('failed to parse kraken response') from exc
