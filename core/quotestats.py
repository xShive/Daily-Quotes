from my_types.quote_types import QuoteHistory
import re


class QuoteStats:
    def __init__(self, history: QuoteHistory):
        self.history = history
    

    def count_quotes_made(self) -> list[tuple[int, int]]:
        result: dict[int, int] = {}

        for quote_chain in self.history:
            for quote_part in quote_chain:      # AUTHOR = 4587654327
                author = quote_part[2]
                result[author] = result.get(author, 0) + 1
        
        # sort by value
        return sorted(result.items(), key=lambda item: item[1], reverse=True)
    

    def count_total_quotes(self, known_users_dict: dict[str, list[str]]) -> list[tuple[str, int]]:
        result: dict[str, int] = {}

        for quote_chain in self.history:
            for quote_part in quote_chain:
                author_data = quote_part[1]

                matches = []
                # Loop through {"Hintrill": ["hintrill", "elias a"], "Sabato": ["sabato", "safloet"]}
                for primary_user, aliases in known_users_dict.items():
                    for alias in aliases:
                        # Find whole words only, case-insensitive
                        match = re.search(r'\b' + re.escape(alias) + r'\b', author_data, re.IGNORECASE)
                        if match:
                            # Save the start index and the PRIMARY user name, not the alias
                            matches.append((match.start(), primary_user))

                if not matches:
                    continue

                # Pick the primary user whose alias appeared FIRST in the author string
                _, matched_primary_user = min(matches, key=lambda pair: pair[0])
                result[matched_primary_user] = result.get(matched_primary_user, 0) + 1

        return sorted(result.items(), key=lambda item: item[1], reverse=True)