from typing import List, Tuple

QuoteLine = Tuple[str, str]     # ("quote", "name")
Quote = List[QuoteLine]         # full chain (one quote tuple)
T_Quote = Tuple[QuoteLine, ...] # full chain but tuples for set operations
QuoteHistory = List[Quote]      # all prepared quotes in a list

RECENTS_SIZE = 50