import string
from math import log2

from src.analyzer.translator import translate_password
from src.analyzer.matches import scan_matches
from src.domain.scanner import ScanType
from src.domain.dataset import Category
from src.domain.entropy import Entropy

# https://www.okta.com/identity-101/password-entropy/ -> https://www.pleacher.com/mp/mlessons/algebra/entropy.html

_base = {
    # tuple : pool
    "lowercase"   : (string.ascii_lowercase, len(string.ascii_lowercase)),
    "uppercase"   : (string.ascii_uppercase, len(string.ascii_uppercase)),
    "numbers"     : (string.digits, len(string.digits)),
    "punctuation" : (string.punctuation, len(string.punctuation)),
    "whitespace"  : (string.whitespace, len(string.whitespace)),
    "ascii"       : (''.join(map(chr, range(32))), 32)
}

def _calculate_pool(password: str) -> int:
    pool: set = set()
    
    for i in range(len(password)):
        for string, seq in _base.values():
            if password[i] in string:
                pool.add((seq, string))
    
    return sum([i[0] for i in list(pool)])

def calculate_entropy(password: str) -> float:
    pool = _calculate_pool(password)
    
    scan, penalty = scan_matches(password=password, scan_category=Category.BLACKLIST, prioritize=ScanType.ALIKE), [1]
    
    if scan["finds"]:
        for find in scan["finds"]:
            penalty.extend(match["attempts"] for match in find["matches"])
        
        if not sum([i["words_found"] for i in scan["finds"]]) > 0: pool = 1
    
    entropy = Entropy(
        bits=log2(pool**len(password)),
        top_attempts=min(penalty) * len(penalty),
        leet_guesses=translate_password(password=password, counter=True)[1],
    )
    
    return entropy.bits * (1 / log2((entropy.top_attempts * entropy.leet_guesses) + 2))
