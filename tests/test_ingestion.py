from src.ingestion.load_candidates import stream_jsonl


def test_stream_jsonl_returns_batches():
    batches = list(stream_jsonl("Data/candidates.jsonl", batch_size=50000))
    assert len(batches) >= 1
    assert len(batches[0]) > 0


def test_stream_jsonl_batch_size():
    batches = list(stream_jsonl("Data/candidates.jsonl", batch_size=100000))
    assert len(batches) == 1


def test_stream_jsonl_first_record_has_candidate_id():
    batches = list(stream_jsonl("Data/candidates.jsonl", batch_size=100000))
    assert "candidate_id" in batches[0][0]


def test_stream_jsonl_all_records_have_id():
    batches = list(stream_jsonl("Data/candidates.jsonl", batch_size=50000))
    all_have_id = all("candidate_id" in r for batch in batches for r in batch)
    assert all_have_id
