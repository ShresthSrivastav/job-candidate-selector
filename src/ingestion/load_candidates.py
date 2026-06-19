from __future__ import annotations
import gzip
import json
from typing import Iterator, List, Dict
from src.utils.logger import info, debug, warning


def stream_jsonl_gz(path: str, batch_size: int = 10000) -> Iterator[List[Dict]]:
    """Stream a gzipped JSONL file line-by-line, yielding batches of dicts."""
    info("Streaming gz JSONL from {} with batch_size={}", path, batch_size)
    batch: List[Dict] = []
    processed = 0
    with gzip.open(path, mode="rt", encoding="utf-8") as fh:
        # Peek a small prefix to detect if this is a JSON array file
        start = fh.read(1024)
        if not start:
            return
        first = start.lstrip()[:1]
        fh.seek(0)
        if first == "[":
            # The file is a JSON array (small sample files). Load and yield in chunks.
            try:
                arr = json.load(fh)
            except Exception as e:
                warning("Failed to parse gz JSON array: {}", e)
                return
            for i in range(0, len(arr), batch_size):
                yield arr[i : i + batch_size]
            return

        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                warning("Failed to parse line as JSON: {}", e)
                continue
            batch.append(obj)
            if len(batch) >= batch_size:
                yield batch
                processed += len(batch)
                debug("Yielded batch, processed={}", processed)
                batch = []
    if batch:
        yield batch
        processed += len(batch)
        debug("Yielded final batch, processed={}", processed)


def stream_jsonl(path: str, batch_size: int = 10000) -> Iterator[List[Dict]]:
    """Stream a plain JSONL file (not gzipped)."""
    info("Streaming JSONL from {} with batch_size={}", path, batch_size)
    batch: List[Dict] = []
    processed = 0
    with open(path, mode="rt", encoding="utf-8") as fh:
        # Peek a small prefix to detect JSON array files
        start = fh.read(1024)
        if not start:
            return
        first = start.lstrip()[:1]
        fh.seek(0)
        if first == "[":
            try:
                arr = json.load(fh)
            except Exception as e:
                warning("Failed to parse JSON array file: {}", e)
                return
            for i in range(0, len(arr), batch_size):
                yield arr[i : i + batch_size]
            return

        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception as e:
                warning("Failed to parse line as JSON: {}", e)
                continue
            batch.append(obj)
            if len(batch) >= batch_size:
                yield batch
                processed += len(batch)
                debug("Yielded batch, processed={}", processed)
                batch = []
    if batch:
        yield batch
        processed += len(batch)
        debug("Yielded final batch, processed={}", processed)
