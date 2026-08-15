import argparse
from argparse import ArgumentParser
from pathlib import Path

from data.registry import resolve_path
from src.analyzer.statistics import measure
from src.analyzer.matches import scan_matches
from src.domain.dataset import Category, Dataset
from src.domain.scanner import ScanType

def _parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="scanner",
        description="Scanner for analyzing passwords."
    )

    parser.add_argument(
        "password",
        help="Password to be analyzed"
    )

    parser.add_argument(
        "--scan-type", "-S",
        dest="scantype",
        type=ScanType,
        default=ScanType.COMPLETE,
        choices=list(ScanType),
        help="Type of scan to perform."
    )

    group = parser.add_mutually_exclusive_group()

    group.add_argument(
        "-c", "--category",
        type=Category,
        default=None,
        choices=list(Category),
        help="Category of datasets to analyze."
    )

    group.add_argument(
        "-p", "--path",
        dest="path",
        type=str,
        help="Dataset path"
    )

    group.add_argument(
        "-d", "--dataset",
        dest="dataset",
        type=str,
        help="Dataset name located in \'data/analysis/\'"
    )
    
    group.add_argument(
        "-dl", "--dataset-list",
        dest="datasets",
        nargs="+",
        help="Path to a custom dataset for analyszis"
    )
    
    group.add_argument(
        "-s", "--statistics",
        dest="stats",
        default=False,
        action="store_true",
        help="Metrify"
    )

    return parser.parse_args()


def scanner_parser() -> None:
    parser = _parser()
    
    if parser.stats:
        scann = measure(scan_matches, password=parser.password, scan_category=parser.category, scan_type=parser.scantype, dataset=parser.dataset, statistic=True)
    
    else:
        scann = scan_matches(password=parser.password, scan_category=parser.category, scan_type=parser.scantype, dataset=parser.dataset)
    
    print(scann)
        