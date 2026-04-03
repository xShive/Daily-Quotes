# ========== Imports ==========
from typing import Optional
from types.quote_types import Quote, T_Quote, QuoteHistory, RECENTS_SIZE


# ========== QuoteCache Class ==========
class QuoteCache:
    """
    RAM cache using a dictionary to access quotes without making API calls.
    Follows the same pattern as AssetCache from League bot :D.
    """
    
    def __init__(self):
        self._quote_history: QuoteHistory = []
        self._recent_dailies: QuoteHistory = []
        self._recents_size: int = RECENTS_SIZE

    def _quote_tuple(self, quote: Quote) -> T_Quote:
        """Convert Quote into a hashable tuple for set operations."""
        return tuple(quote)

    def get_quote_history(self, daily=False) -> QuoteHistory:
        """
        Get cached quote history.

        - daily=False: return ALL cached history
        - daily=True: return history excluding recent picks, avoiding repeated quotes

        This uses hashable keys from quote content and avoids O(n^2) loops.
        """
        if not daily:
            return self._quote_history

        recent_tuples = {self._quote_tuple(q) for q in self._recent_dailies}
        return [q for q in self._quote_history if self._quote_tuple(q) not in recent_tuples]

    def cache_quote_history(self, all_quotes: QuoteHistory):
        """
        Save quotes into the cache.
        All given arguments will be appended to the cache.
        """
        for quote in all_quotes:
            self._quote_history.append(quote)
    
    def cache_recent_history(self, quote: Quote):
        """
        Save a single quote into recent history (MRU queue).

        The most recent quote is index 0. The list stays unique and capped at _recents_size.
        """
        self._recent_dailies.insert(0, quote)
        self._recent_dailies.pop()

    def edit_recents_size(self, size: int):
        """
        Changes the amount of recent quotes to be stored in the cache.

        If recents are reduced, older entries are dropped to conform to new size.
        """
        self._recents_size = size
        while len(self._recent_dailies) > self._recents_size:
            self._recent_dailies.pop()

    def clear_cache(self):
        """
        Delete all cache.
        """
        self._quote_history.clear()