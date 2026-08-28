import re
ans = """The NAV of ICICI Prudential Multicap Fund – Direct Growth as of 26 Aug '26 is ₹991.42.
Source: https://groww.in/mutual-funds/icici-prudential-multicap-fund-direct-growth | Last updated: 2026-08-27"""

print("Ans before:")
print(repr(ans))
answer_match = re.split(r"\n*\s*Source:", ans, flags=re.IGNORECASE)
print(answer_match)
