"""Parser tests against fixtures copied from the sources' own documentation.

The MGF, GNPS-JSON and MassBank fixtures reproduce field layouts published in
GNPS's and MassBank's official docs, so these tests check real format
handling, not a shape SPECGAP invented for its own convenience.
"""
import os
import sys

FIXTURES = os.path.join(os.path.dirname(__file__), "fixtures")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from specgap.parsers import (  # noqa: E402
    is_natural_product,
    parse_gnps_json,
    parse_massbank_stream,
    parse_mgf,
    parse_msp,
    parse_sdf,
)


def fixture(name):
    return open(os.path.join(FIXTURES, name), encoding="utf-8")


# ---------------------------------------------------------------- MGF


def test_mgf_parses_both_records():
    with fixture("gnps_sample.mgf") as fh:
        entries = list(parse_mgf(fh))
    assert len(entries) == 2
    assert [e.spectrum_id for e in entries] == [
        "CCMSLIB00000077995", "CCMSLIB00000072100"]


def test_mgf_captures_metadata():
    with fixture("gnps_sample.mgf") as fh:
        first = next(parse_mgf(fh))
    assert first.source == "GNPS"
    assert first.ion_mode == "positive"
    assert first.library_quality == "1"
    assert first.ms_level == "2"
    assert first.smiles.startswith("C1=CN=CC(=N1)")


def test_mgf_treats_na_as_null():
    """GNPS writes the literal string 'N/A'; it must not become a value."""
    with fixture("gnps_sample.mgf") as fh:
        entries = list(parse_mgf(fh))
    assert entries[0].inchi is None      # INCHI=N/A
    assert entries[1].smiles is None     # SMILES=N/A


def test_mgf_has_no_inchikey():
    """Documents a real GNPS MGF limitation: no InChIKey field exists."""
    with fixture("gnps_sample.mgf") as fh:
        entries = list(parse_mgf(fh))
    assert all(e.inchikey is None for e in entries)


def test_mgf_counts_peaks():
    with fixture("gnps_sample.mgf") as fh:
        entries = list(parse_mgf(fh))
    assert entries[0].n_peaks == 3
    assert entries[1].n_peaks == 3


# ----------------------------------------------------------- MassBank


def test_massbank_parses_all_records():
    with fixture("massbank_sample.txt") as fh:
        entries = list(parse_massbank_stream(fh))
    assert len(entries) == 3
    assert entries[0].spectrum_id == "MSBNK-AAFC-AC000101"


def test_massbank_captures_iterative_ch_name():
    """CH$NAME is iterative in the spec; every synonym must be captured."""
    with fixture("massbank_sample.txt") as fh:
        first = next(parse_massbank_stream(fh))
    assert first.names == ["Dehydrocostus lactone", "Epiligulyl oxide"]
    assert first.primary_name == "Dehydrocostus lactone"


def test_massbank_parses_chlink_inchikey_subtag():
    with fixture("massbank_sample.txt") as fh:
        first = next(parse_massbank_stream(fh))
    # must pick INCHIKEY specifically, not CAS or PUBCHEM which precede/follow
    assert first.inchikey == "NETSQGRTUNRXEO-UHFFFAOYSA-N"


def test_massbank_parses_ion_mode_subtag():
    with fixture("massbank_sample.txt") as fh:
        entries = list(parse_massbank_stream(fh))
    assert entries[0].ion_mode == "positive"
    assert entries[2].ion_mode == "negative"


def test_massbank_missing_inchikey_is_none_not_error():
    with fixture("massbank_sample.txt") as fh:
        entries = list(parse_massbank_stream(fh))
    assert entries[2].inchikey is None


def test_massbank_natural_product_class_is_anchored():
    """'Non-Natural Product' must not match a naive substring test."""
    with fixture("massbank_sample.txt") as fh:
        entries = list(parse_massbank_stream(fh))
    assert is_natural_product(entries[0]) is True    # 'Natural Product; ...'
    assert is_natural_product(entries[1]) is False   # 'Non-Natural Product; ...'
    assert is_natural_product(entries[2]) is True


def test_massbank_captures_per_record_license():
    with fixture("massbank_sample.txt") as fh:
        entries = list(parse_massbank_stream(fh))
    assert entries[0].license == "CC BY"
    assert entries[1].license == "CC BY-NC"


# ---------------------------------------------------------------- SDF


def test_sdf_parses_all_records():
    with fixture("coconut_sample.sdf") as fh:
        entries = list(parse_sdf(fh))
    assert len(entries) == 4
    assert entries[0].structure_id == "CNP0138595.0"


def test_sdf_captures_inchikey_and_names():
    with fixture("coconut_sample.sdf") as fh:
        first = next(parse_sdf(fh))
    assert first.inchikey == "NETSQGRTUNRXEO-UHFFFAOYSA-N"
    assert first.primary_name == "Dehydrocostus lactone"
    assert "Epiligulyl oxide" in first.names


def test_sdf_splits_semicolon_multivalue_fields():
    with fixture("coconut_sample.sdf") as fh:
        first = next(parse_sdf(fh))
    assert "Saussurea lappa" in first.organisms
    assert "Aucklandia lappa" in first.organisms


def test_sdf_record_without_inchikey_still_emitted():
    with fixture("coconut_sample.sdf") as fh:
        entries = list(parse_sdf(fh))
    last = entries[-1]
    assert last.structure_id == "CNP0215845.0"
    assert last.inchikey is None


# ---------------------------------------------------------------- MSP


def test_msp_parses_all_records():
    with fixture("mona_sample.msp") as fh:
        entries = list(parse_msp(fh))
    assert len(entries) == 4


def test_msp_captures_inchikey_and_synonyms():
    with fixture("mona_sample.msp") as fh:
        first = next(parse_msp(fh))
    assert first.inchikey == "NETSQGRTUNRXEO-UHFFFAOYSA-N"
    assert first.names == ["Dehydrocostus lactone", "Epiligulyl oxide"]


def test_msp_na_name_is_dropped():
    with fixture("mona_sample.msp") as fh:
        entries = list(parse_msp(fh))
    assert entries[2].primary_name is None


def test_msp_uses_declared_num_peaks():
    with fixture("mona_sample.msp") as fh:
        first = next(parse_msp(fh))
    assert first.n_peaks == 3


# ---------------------------------------------------------- GNPS JSON


def test_gnps_json_parses_array():
    with fixture("gnps_sample.json") as fh:
        entries = list(parse_gnps_json(fh))
    assert len(entries) == 2
    assert entries[0].spectrum_id == "CCMSLIB00000579358"


def test_gnps_json_strips_padded_ion_mode():
    """GNPS's own documented example has ' Negative' with a leading space."""
    with fixture("gnps_sample.json") as fh:
        first = next(parse_gnps_json(fh))
    assert first.ion_mode == "negative"


def test_gnps_json_unquotes_inchi():
    with fixture("gnps_sample.json") as fh:
        first = next(parse_gnps_json(fh))
    assert first.inchi.startswith("InChI=1S/C7H8N4O2")


def test_gnps_json_counts_peaks_from_peaks_json():
    with fixture("gnps_sample.json") as fh:
        entries = list(parse_gnps_json(fh))
    assert entries[0].n_peaks == 2
    assert entries[1].n_peaks == 1


# ------------------------------------------- MoNA real-format regressions


def test_msp_normalizes_single_letter_ion_modes():
    """MoNA writes 'P'/'N', MassBank 'POSITIVE'/'NEGATIVE', GNPS ' Negative'.
    Without normalization these become four modes for two physical states.
    Found against a real MoNA experimental export record.
    """
    import io
    from specgap.parsers import parse_msp
    msp = ("Name: A\nDB#: 1\nInChIKey: JFPVXVDWJQMJEE-IZRZKJBUSA-N\n"
           "Ion_mode: N\nNum Peaks: 1\n100 1\n\n"
           "Name: B\nDB#: 2\nInChIKey: MUMGGOZAMZWBJJ-DYKIIFRCSA-N\n"
           "Ion_mode: P\nNum Peaks: 1\n100 1\n")
    modes = [e.ion_mode for e in parse_msp(io.StringIO(msp))]
    assert modes == ["negative", "positive"]


def test_msp_captures_spectrum_type_as_ms_level():
    """MoNA marks MS1 vs MS2 in Spectrum_type. MS1 gives a mass, not a
    fragmentation fingerprint, so the level must be available for filtering.
    """
    import io
    from specgap.parsers import parse_msp
    msp = ("Name: A\nDB#: 1\nInChIKey: JFPVXVDWJQMJEE-IZRZKJBUSA-N\n"
           "Spectrum_type: MS1\nNum Peaks: 1\n100 1\n")
    assert next(parse_msp(io.StringIO(msp))).ms_level == "MS1"


def test_msp_reads_inchikey_from_real_mona_layout():
    """Field order and the Comments blob from an actual MoNA record."""
    import io
    from specgap.parsers import parse_msp
    msp = ('Name: Cefuroxime\nSynon: $:00in-source\nDB#: WA002994\n'
           'InChIKey: JFPVXVDWJQMJEE-IZRZKJBUSA-N\nSpectrum_type: MS1\n'
           'Ion_mode: N\nFormula: C16H16N4O8S\n'
           'Comments: "SMILES=CO/N=C(/C1=CC=CO1)" "cas=55268-75-2" "license=CC BY-NC"\n'
           'Num Peaks: 2\n100 3.1\n101 1.2\n')
    e = next(parse_msp(io.StringIO(msp)))
    assert e.inchikey == "JFPVXVDWJQMJEE-IZRZKJBUSA-N"
    assert e.primary_name == "Cefuroxime"
    assert e.n_peaks == 2


# ------------------------------------------------- LOTUS CSV (structures)


def test_lotus_csv_aggregates_rows_into_distinct_structures():
    """LOTUS ships one row per (structure, organism, reference) triple.
    Emitting one entry per row would count a compound found in fifty
    organisms fifty times and inflate every coverage denominator.
    """
    from specgap.parsers import parse_lotus_csv
    entries = list(parse_lotus_csv(
        os.path.join(FIXTURES, "lotus_sample.csv"), verbose=False))
    assert len(entries) == 2          # from 5 rows
    keys = {e.inchikey for e in entries}
    assert keys == {"NETSQGRTUNRXEO-UHFFFAOYSA-N", "HZGJWEZZXLGUAU-UHFFFAOYSA-N"}


def test_lotus_csv_merges_names_and_organisms():
    from specgap.parsers import parse_lotus_csv
    entries = {e.inchikey: e for e in parse_lotus_csv(
        os.path.join(FIXTURES, "lotus_sample.csv"), verbose=False)}
    e = entries["NETSQGRTUNRXEO-UHFFFAOYSA-N"]
    assert e.names == ["Dehydrocostus lactone", "Epiligulyl oxide"]
    assert len(e.organisms) == 3


def test_lotus_csv_skips_rows_without_inchikey():
    from specgap.parsers import parse_lotus_csv
    entries = list(parse_lotus_csv(
        os.path.join(FIXTURES, "lotus_sample.csv"), verbose=False))
    assert all(e.inchikey for e in entries)


# --------------------------------------- GNPS JSON structure identifiers


def test_gnps_json_reads_inchikey_from_smiles_derived_field():
    """GNPS JSON carries InChIKey_smiles / InChIKey_inchi, which is why GNPS
    can be audited via JSON but not via MGF (no key field at all there).
    """
    import io, json
    from specgap.parsers import parse_gnps_json
    recs = [{"spectrum_id": "A", "Compound_Name": "X",
             "InChIKey_smiles": "NETSQGRTUNRXEO-UHFFFAOYSA-N",
             "library_membership": "GNPS-LIBRARY", "peaks_json": "[[1,2]]"}]
    e = next(parse_gnps_json(io.StringIO(json.dumps(recs))))
    assert e.inchikey == "NETSQGRTUNRXEO-UHFFFAOYSA-N"


def test_gnps_json_falls_back_to_inchi_derived_key():
    import io, json
    from specgap.parsers import parse_gnps_json
    recs = [{"spectrum_id": "B", "Compound_Name": "Y",
             "InChIKey_inchi": "HZGJWEZZXLGUAU-UHFFFAOYSA-N",
             "library_membership": "GNPS-LIBRARY", "peaks_json": "[]"}]
    e = next(parse_gnps_json(io.StringIO(json.dumps(recs))))
    assert e.inchikey == "HZGJWEZZXLGUAU-UHFFFAOYSA-N"


def test_gnps_json_captures_library_membership_for_propagated_filter():
    """GNPS_PROPOGATED spectra are computationally propagated, not measured,
    and must be excludable before reporting coverage."""
    import io, json
    from specgap.parsers import parse_gnps_json
    recs = [{"spectrum_id": "C", "Compound_Name": "Z",
             "InChIKey_smiles": "NETSQGRTUNRXEO-UHFFFAOYSA-N",
             "library_membership": "GNPS_PROPOGATED", "peaks_json": "[]"}]
    e = next(parse_gnps_json(io.StringIO(json.dumps(recs))))
    assert "PROPOGATED" in (e.compound_class or "").upper()
