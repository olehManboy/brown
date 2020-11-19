import itertools
import threading
import time
from typing import Dict, Generator

import requests

from .bases import BlockGasStrategy, SimpleGasStrategy, TimeGasStrategy

_gasnow_update = 0
_gasnow_data: Dict[str, int] = {}
_gasnow_lock = threading.Lock()


def _fetch_gasnow(key: str) -> int:
    global _gasnow_update
    with _gasnow_lock:
        if time.time() - _gasnow_update > 15:
            data = None
            for i in range(12):
                response = requests.get(
                    "https://www.gasnow.org/api/v3/gas/price?utm_source=brownie"
                )
                if response.status_code != 200:
                    time.sleep(5)
                    continue
                data = response.json()["data"]
                break
            if data is None:
                raise ValueError
            _gasnow_update = data.pop("timestamp") // 1000
            _gasnow_data.update(data)

    return _gasnow_data[key]


class LinearScalingStrategy(TimeGasStrategy):
    """
    Gas strategy for linear gas price increase.

    Arguments
    ---------
    initial_gas_price : int
        The initial gas price to use in the first transaction
    max_gas_price : int
        The maximum gas price to use
    increment : float
        Multiplier applied to the previous gas price in order to determine the new gas price
    time_duration : int
        Number of seconds between transactions
    """

    def __init__(
        self,
        initial_gas_price: int,
        max_gas_price: int,
        increment: float = 1.125,
        time_duration: int = 30,
    ):
        super().__init__(time_duration)
        self.initial_gas_price = initial_gas_price
        self.max_gas_price = max_gas_price
        self.increment = increment

    def get_gas_price(self) -> Generator[int, None, None]:
        last_gas_price = self.initial_gas_price
        yield last_gas_price

        while True:
            last_gas_price = min(int(last_gas_price * self.increment), self.max_gas_price)
            yield last_gas_price


class ExponentialScalingStrategy(TimeGasStrategy):
    """
    Gas strategy for exponential increasing gas prices.

    The gas price for each subsequent transaction is calculated as the previous price
    multiplied by `1.1 ** n` where n is the number of transactions that have been broadcast.
    In this way the price increase starts gradually and ramps up until confirmation.

    Arguments
    ---------
    initial_gas_price : int
        The initial gas price to use in the first transaction
    max_gas_price : int
        The maximum gas price to use
    increment : float
        Multiplier applied to the previous gas price in order to determine the new gas price
    time_duration : int
        Number of seconds between transactions
    """

    def __init__(
        self, initial_gas_price: int, max_gas_price: int, time_duration: int = 30,
    ):
        super().__init__(time_duration)
        self.initial_gas_price = initial_gas_price
        self.max_gas_price = max_gas_price

    def get_gas_price(self) -> Generator[int, None, None]:
        last_gas_price = self.initial_gas_price
        yield last_gas_price

        for i in itertools.count(1):
            last_gas_price = int(last_gas_price * 1.1 ** i)
            yield min(last_gas_price, self.max_gas_price)


class GasNowStrategy(SimpleGasStrategy):
    """
    Gas strategy for determing a price using the GasNow API.

    GasNow returns 4 possible prices:

    rapid: the median gas prices for all transactions currently included
           in the mining block
    fast: the gas price transaction "N", the minimum priced tx currently
          included in the mining block
    standard: the gas price of the Max(2N, 500th) transaction in the mempool
    slow: the gas price of the max(5N, 1000th) transaction within the mempool

    Visit https://www.gasnow.org/ for more information on how GasNow
    calculates gas prices.
    """

    def __init__(self, speed: str = "fast"):
        if speed not in ("rapid", "fast", "standard", "slow"):
            raise ValueError("`speed` must be one of: rapid, fast, standard, slow")
        self.speed = speed

    def get_gas_price(self) -> int:
        return _fetch_gasnow(self.speed)


class GasNowScalingStrategy(BlockGasStrategy):
    """
    Block based scaling gas strategy using the GasNow API.

    The initial gas price is set according to `initial_speed`. The gas price
    for each subsequent transaction is increased by multiplying the previous gas
    price by `increment`, or increasing to the current `initial_speed` gas price,
    whichever is higher. No repricing occurs if the new gas price would exceed
    the current `max_speed` price as given by the API.
    """

    def __init__(
        self,
        initial_speed: str = "standard",
        max_speed: str = "rapid",
        increment: float = 1.125,
        block_duration: int = 2,
    ):
        super().__init__(block_duration)
        if initial_speed not in ("rapid", "fast", "standard", "slow"):
            raise ValueError("`initial_speed` must be one of: rapid, fast, standard, slow")
        self.initial_speed = initial_speed
        self.max_speed = max_speed
        self.increment = increment

    def get_gas_price(self) -> Generator[int, None, None]:
        last_gas_price = _fetch_gasnow(self.initial_speed)
        yield last_gas_price

        while True:
            # increment the last price by `increment` or use the new
            # `initial_speed` value, whichever is higher
            initial_gas_price = _fetch_gasnow(self.initial_speed)
            incremented_gas_price = int(last_gas_price * self.increment)
            new_gas_price = max(initial_gas_price, incremented_gas_price)

            # do not exceed the current `max_speed` price
            max_gas_price = _fetch_gasnow(self.max_speed)
            last_gas_price = min(max_gas_price, new_gas_price)
            yield last_gas_price
