import unicodedata
from difflib import SequenceMatcher, Match
from typing import Callable, Optional, Union

from src.analyzer.translator import translate_password, translate_candidates
from src.domain.scanner import ScanType
from src.domain.dataset import Dataset
from src.domain.models.scanner import ScannerFinds, ScannerResult

def _normalize(word: str) -> str:
    return unicodedata.normalize("NFKD", word.lower().strip()).encode("ASCII", "ignore").decode("ASCII")

def scan(
        password: str, 
        base: list[str], 
        dataset: Dataset,
        scan_type: Union[ScanType, list[ScanType]] = ScanType.COMPLETE,
        prioritize: Optional[Union[ScanType, set[ScanType]]] = None
    ) -> ScannerResult:
    
    if not password:
        raise ValueError("password cannot be empty")
    
    if prioritize is ScanType.COMPLETE:
        raise TypeError("ScanType prioritizer cannot be COMPLETE")
    
    attempts: int = 0
    words: list[ScannerFinds] = list()
    
    acc: float = 0
    amp: float = max(0.5, min(2.0, 7 / len(password)))
    
    nor_password: str = _normalize(password)

    result: ScannerResult = {
        "matches"  : [],
        "score"    : 0,
        "attempts" : 0,
    }
    
    def global_attempts() -> None:
        nonlocal result
        result["attempts"] += 1

    def internal_attempts() -> int:
        nonlocal attempts
        return attempts

    def scan_regular(word: str, nor_word: str) -> bool:
        nonlocal dataset
        nonlocal words
        nonlocal acc

        global_attempts()

        if password.lower() == word.lower():
            acc += 100
            words.append({"word" : word, "scan_type" : ScanType.REGULAR.value, "dataset" : dataset.filename, "attempts" : internal_attempts()})
            return True

        elif nor_password == nor_word:
            acc += 80 * amp
            words.append({"word" : word, "scan_type" : ScanType.REGULAR.value, "dataset" : dataset.filename, "attempts" : internal_attempts()})
            return True

        return False
    
    def scan_sequence(word: str, nor_word: str) -> bool:
        nonlocal attempts
        nonlocal dataset
        nonlocal words
        nonlocal acc
        
        global_attempts()

        if nor_password in nor_word or nor_word in nor_password:
            acc += 60 * amp
            words.append({"word" : word, "scan_type" : ScanType.SEQUENCE.value, "dataset" : dataset.filename, "attempts" : internal_attempts()})
            return True
        
        return False

    def scan_pattern(word: str, nor_word: str) -> bool:
        nonlocal attempts
        nonlocal dataset
        nonlocal words
        nonlocal acc
        
        global_attempts()

        def match_analyzer(str1: str, str2: str) -> float:
            smal: int = min(len(str1), len(str2))

            if smal == 0: return 0
            if abs(len(str1) - len(str2)) > 3: return 0

            matcher: SequenceMatcher = SequenceMatcher(None, str1, str2)
            matchh: Match = matcher.find_longest_match(0, len(str1), 0, len(str2))

            limit_n: int = 4

            if smal < limit_n:
                if matchh.size != smal: return 0

            else:
                if matchh.size < limit_n:    return 0
                if matchh.size < smal * 0.8: return 0

            return matchh.size / smal

        score: float = max(match_analyzer(password.lower(), word.lower()), match_analyzer(nor_password, nor_word))

        if score > 0:
            acc += score * 60 * amp
            words.append({"word" : word, "scan_type" : ScanType.PATTERN.value, "dataset" : dataset.filename, "attempts" : internal_attempts()})
            return True
        
        return False

    def scan_alike(word: str, nor_word: str) -> bool:
        nonlocal attempts
        nonlocal dataset
        nonlocal words
        nonlocal acc

        global_attempts()
        
        if translate_password(nor_word) in translate_candidates(nor_password):
            acc += 60 * amp
            words.append({"word" : word, "scan_type" : ScanType.ALIKE.value, "dataset" : dataset.filename, "attempts" : internal_attempts()})
            return True
        
        return False
    
    def _scann_sequence(scanners: dict[ScanType, Callable]) -> list[Callable[[str, str], bool]]:
        priorities: list[Callable[[str, str], bool]] = list()
        
        for i in list(prioritize) if type(prioritize) is set else [prioritize]:
            if i in [scan_type] if type(scan_type) is ScanType else scan_type:
                priorities.append(scanners[i])
        
        return priorities
    
    scanners: dict[ScanType, Callable[[str, str], bool]] = {
        ScanType.SEQUENCE : scan_sequence,
        ScanType.PATTERN  : scan_pattern,
        ScanType.ALIKE    : scan_alike,
    }
    
    defs: list[Callable[[str, str], bool]] = _scann_sequence(scanners=scanners)
    
    for word in base:
        nor_word: str = _normalize(word)
        attempts += 1

        if scan_regular(word, nor_word): continue
        for fun in defs:
            if fun(word, nor_word): break

    result["score"], result["matches"] = acc, words

    return result
