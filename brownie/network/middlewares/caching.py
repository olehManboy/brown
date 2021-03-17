import json
import threading
import time
from collections import OrderedDict
from typing import Callable, Dict, List, Optional

from web3 import Web3

from brownie.network.middlewares import BrownieMiddlewareABC


class RequestCachingMiddleware(BrownieMiddlewareABC):

    """
    Web3 middleware for request caching.
    """

    def __init__(self, w3: Web3) -> None:
        self.w3 = w3

        latest = w3.eth.getBlock("latest")
        self.last_block = latest.hash
        self.last_block_seen = latest.timestamp
        self.last_request = 0.0
        self.block_cache: OrderedDict = OrderedDict()
        self.block_filter = w3.eth.filter("latest")

        self.lock = threading.Lock()
        self.event = threading.Event()
        threading.Thread(target=self.block_filter_loop, daemon=True).start()

    @classmethod
    def get_layer(cls, w3: Web3, network_type: str) -> Optional[int]:
        if network_type == "live":
            return 0
        else:
            return None

    @property
    def time_since(self) -> float:
        return time.time() - self.last_request

    def block_filter_loop(self) -> None:
        while True:
            # if the last RPC request was > 60 seconds ago, reduce the rate of updates.
            # we eventually settle at one query per minute after 10 minutes of no requests.
            with self.lock:
                if self.time_since > 60:
                    self.block_cache.clear()
                    self.event.clear()
            while self.time_since > 60:
                self.event.wait(min(self.time_since / 10, 60))

            # query the filter for new blocks
            with self.lock:
                try:
                    new_blocks = self.block_filter.get_new_entries()
                except AttributeError:
                    return
                if new_blocks:
                    self.block_cache[new_blocks[-1]] = {}
                    self.last_block = new_blocks[-1]
                    self.last_block_seen = time.time()
                    if len(self.block_cache) > 5:
                        old_key = list(self.block_cache)[0]
                        del self.block_cache[old_key]

            if new_blocks and self.time_since < 15:
                # if this update found a new block and we've been querying
                # frequently, we can wait a few seconds before the next update
                time.sleep(5)
            elif time.time() - self.last_block_seen < 15:
                # if it's been less than 15 seconds since the last block, wait 2 seconds
                time.sleep(2)
            else:
                # if it's been more than 15 seconds, only wait 1 second
                time.sleep(1)

    def process_request(self, make_request: Callable, method: str, params: List) -> Dict:
        # do not apply this middleware to filter updates or we'll die recursion death
        if method in ("eth_getFilterChanges", "eth_uninstallFilter"):
            return make_request(method, params)

        # try to return a cached value
        param_str = json.dumps(params, separators=(",", ""), default=str)
        with self.lock:
            self.last_request = time.time()
            self.event.set()
            try:
                return self.block_cache[self.last_block][method][param_str]
            except KeyError:
                pass

        # cached value is unavailable, make a request and cache the result
        with self.lock:
            response = make_request(method, params)
            self.block_cache.setdefault(self.last_block, {}).setdefault(method, {})
            self.block_cache[self.last_block][method][param_str] = response
        return response

    def uninstall(self) -> None:
        if self.w3.provider:
            self.w3.eth.uninstallFilter(self.block_filter.filter_id)
