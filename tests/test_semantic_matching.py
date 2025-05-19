import json
import pathlib
import pytest
import httpx

from backend.services.nlp_utils import mentions_drug
from backend.services import openfda_service as ofs


# ----------------------------------------------------------------------
# unit tests for mentions_drug()
# ----------------------------------------------------------------------
@pytest.mark.parametrize(
    ("text", "drug", "expected"),
    [
        ("Ibuprofen may interact with warfarin.", "ibuprofen", True),
        ("IBUPROFENS increase risk", "ibuprofen", True),           # plural / case
        ("Avoid ibuprofen-based analgesics.", "ibuprofen", True),  # punctuation suffix
        ("This label only mentions aspirin.", "ibuprofen", False),
        ("foobar", "ibuprofen", False),
    ],
)
def test_mentions_drug(text, drug, expected):
    assert mentions_drug(text, drug) is expected


# ----------------------------------------------------------------------
# integration test for OpenFDAService.get_interactions()
# ----------------------------------------------------------------------
@pytest.fixture(scope="session")
def dummy_label():
    data_path = pathlib.Path(__file__).parent / "data" / "sample_label.json"
    return json.loads(data_path.read_text())


@pytest.mark.asyncio
async def test_get_interactions(monkeypatch, dummy_label):
    """Validate the full NLP-driven pipeline without hitting the real API."""

    async def _fake_fetch_label(self, generic):
        return dummy_label

    # Patch the private fetcher on the service class
    monkeypatch.setattr(
        ofs.OpenFDAService, "_fetch_label", _fake_fetch_label, raising=True
    )

    async with httpx.AsyncClient() as client:
        service = ofs.OpenFDAService(client)
        interactions = await service.get_interactions(
            ["ibuprofen", "warfarin", "aspirin"]
        )

    # ----- assertions --------------------------------------------------

    # Represent each interaction as an *unordered* frozenset of the two drugs
    returned_pairs = {
        frozenset((d["drugA"], d["drugB"])) for d in interactions
    }

    # We only *require* these two pairs to be present
    expected_pairs = {
        frozenset({"ibuprofen", "warfarin"}),
        frozenset({"ibuprofen", "aspirin"}),
    }

    assert expected_pairs.issubset(returned_pairs)

    # Spot-check that the warfarin summary still mentions both drug names
    for d in interactions:
        if {"ibuprofen", "warfarin"} == set((d["drugA"], d["drugB"])):
            summary_lc = d["summary"].lower()
            assert "ibuprofen" in summary_lc and "warfarin" in summary_lc
            break
    else:
        pytest.fail("ibuprofen–warfarin pair not found in interactions")
