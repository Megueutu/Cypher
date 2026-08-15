from pathlib import Path
from typing import Optional, Union

from data.registry import get_datasets, resolve_path
from src.domain.scanner import ScanType
from src.domain.dataset import Category, Dataset
from src.analyzer.scanner import scan
from src.domain.models.matches import ScanMatches, FormatScan, Matches

_CACHE: dict[Path, list[str]] = {}

def _severity_analyzer(severity: float) -> str:
    if   severity <=  0: return "No risk detected"
    elif severity <= 10: return "Very low risk"
    elif severity <= 20: return "Low risk"
    elif severity <= 30: return "Moderately low risk"
    elif severity <= 40: return "Moderate risk"
    elif severity <= 50: return "Moderately high risk, should improve"
    elif severity <= 60: return "Average risk, should improve"
    elif severity <= 70: return "High risk, should improve"
    elif severity <= 80: return "Risky password, needs to improve"
    elif severity <= 90: return "Very high risk, needs to improve"
    return "Unprotected; dangerous password, needs to improve"

def load_base(path: Path) -> list[str]:
    if path not in _CACHE:
        with open(path, encoding="utf-8") as file:
            _CACHE[path] = [line.strip() for line in file if line.strip()]
            
    return _CACHE[path]

def find_exactly(
        password: str,
        dataset: Dataset,
        scan_type: Union[ScanType, list[ScanType]],
        prioritize: Optional[Union[ScanType, set[ScanType]]] = None,
    ) -> tuple[int, Matches]:
    
    matches: Matches = {
        "matches"  : [],
        "severity" : [],
    }
    base = load_base(resolve_path(dataset))

    scann = scan(password=password, base=base, scan_type=scan_type, dataset=dataset, prioritize=prioritize)

    matches["matches"] = scann["matches"]
    matches["severity"].append(scann["score"])

    return len(scann["matches"]), matches

def scan_matches(
        password: str,
        dataset: Optional[Union[Dataset, list[Dataset]]] = None,
        path: Optional[Union[Path, str]] = None,
        scan_category: Optional[Category] = None, 
        scan_type: Union[ScanType, list[ScanType]] = ScanType.COMPLETE,
        prioritize: Optional[Union[ScanType, set[ScanType]]] = None,
        statistic: bool = False
    ) -> Union[ScanMatches, tuple[ScanMatches, list[Dataset]]]:
    
    if not password:
        raise ValueError("password cannot be empty")

    finds:    list[FormatScan] = list()
    severity: list[float] = list()
    
    if path is not None:
        raise NotImplementedError("custom dataset paths are not supported yet")
    
    datasets: list[Dataset] 
    if dataset is None: datasets = get_datasets(scan_category)
    elif isinstance(dataset, list): datasets = dataset
    else: datasets = [dataset]
    
    if not datasets:
        if scan_category:
            raise TypeError(f"No datasets were founded with this category: {scan_category}")
        raise ValueError(f"No datasets were given as a parameter")

    for dataset in datasets:
        scan_result = find_exactly(password=password, dataset=dataset, scan_type=scan_type, prioritize=prioritize)
        format_scan: FormatScan = {
            "words_found" : scan_result[0],
            "matches"     : scan_result[1]["matches"],
            "severity"    : round(sum(scan_result[1]["severity"]), 2),
        }
        
        if format_scan["words_found"] > 0:
            severity.extend(scan_result[1]["severity"])
            finds.append(format_scan)

    pctg_severity:  float = round(sum(severity) / max(len(severity), 1), 2)

    answer: ScanMatches = {
        "unprotected" : True if sum(k["words_found"] for k in finds) else False,
        "severity"    : {"percentage" : pctg_severity, "analysis" : _severity_analyzer(pctg_severity)},
        "finds"       : finds if finds else None,
    }
    
    return (answer, datasets) if statistic else answer
