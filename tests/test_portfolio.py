# This file is part of the
#   Garpar Project (https://github.com/quatrope/garpar).
# Copyright (c) 2021, 2022, Nadia Luczywo, Juan Cabral and QuatroPe
# License: MIT
#   Full Text: https://github.com/quatrope/garpar/blob/master/LICENSE


# =============================================================================
# IMPORTS
# =============================================================================

import attr

from garpar.portfolio import GARPAR_METADATA_KEY, Metadata, Portfolio

import pandas as pd

import pytest


# =============================================================================
# TESTS
# =============================================================================


def test_Portfolio_creation():

    df = pd.DataFrame({"stock": [1, 2, 3, 4, 5]})
    df.attrs[GARPAR_METADATA_KEY] = Metadata(
        {
            "entropy": 0.5,
            "window_size": 5,
        }
    )

    manual_pf = Portfolio(df=df.copy())

    mk_pf = Portfolio.from_dfkws(
        df=df,
        entropy=0.5,
        window_size=5,
    )

    assert manual_pf == mk_pf


def test_Portfolio_copy_eq_ne():
    pf = Portfolio.from_dfkws(
        df=pd.DataFrame({"stock": [1, 2, 3, 4, 5]}),
        entropy=0.5,
        window_size=5,
    )
    copy = pf.copy()

    assert pf == copy
    assert pf is not copy
    assert (
        pf._df.attrs[GARPAR_METADATA_KEY]
        == copy._df.attrs[GARPAR_METADATA_KEY]
    )
    assert (
        pf._df.attrs[GARPAR_METADATA_KEY]
        is not copy._df.attrs[GARPAR_METADATA_KEY]
    )

    other = Portfolio.from_dfkws(
        df=pd.DataFrame({"stock": [1, 2, 3, 4, 5]}),
        entropy=0.25,
        window_size=5,
    )

    assert pf != other


def test_Portfolio_bad_metadata():
    df = pd.DataFrame({"stock": [1, 2, 3, 4, 5]})
    df.attrs[GARPAR_METADATA_KEY] = None

    with pytest.raises(TypeError):
        Portfolio(df)


def test_Portfolio_access_df():
    pf = Portfolio.from_dfkws(
        df=pd.DataFrame({"stock": [1, 2, 3, 4, 5]}),
        initial_prices=pd.Series({"stock": [1]}),
        entropy=0.5,
        window_size=5,
    )

    pd.testing.assert_frame_equal(pf.describe(), pf._df.describe())


def test_Portfolio_dir():
    pf = Portfolio.from_dfkws(
        df=pd.DataFrame({"stock": [1, 2, 3, 4, 5]}),
        initial_prices=pd.Series({"stock": [1]}),
        entropy=0.5,
        window_size=5,
    )

    pf_dir = dir(pf)
    df_dir = dir(pf._df)
    meta_dir = attr.asdict(pf._df.attrs[GARPAR_METADATA_KEY])

    assert set(pf_dir).issuperset(df_dir)
    assert set(pf_dir).issuperset(meta_dir)


def test_Portfolio_repr():
    pf = Portfolio.from_dfkws(
        df=pd.DataFrame({"stock": [1, 2, 3, 4, 5]}),
        initial_prices=pd.Series({"stock": [1]}),
        entropy=0.5,
        window_size=5,
    )

    expected = (
        "   stock\n"
        "0      1\n"
        "1      2\n"
        "2      3\n"
        "3      4\n"
        "4      5\n"
        "Portfolio [5 days x 1 stocks]"
    )

    result = repr(pf)
    assert result == expected


@pytest.mark.xfail
def test_Portfolio_to_dataframe():
    pf = Portfolio.from_dfkws(
        df=pd.DataFrame(
            {"stock0": [1, 2, 3, 4, 5], "stock1": [10, 20, 30, 40, 50]},
        ),
        initial_prices=pd.Series({"stock0": [1], "stock1": [10]}),
        entropy=0.5,
        window_size=5,
    )

    expected = pd.DataFrame(
        {
            "stock0": [1, 5, 0.5, 1, 2, 3, 4, 5],
            "stock1": [10, 5, 0.5, 10, 20, 30, 40, 50],
        },
        index=["initial_price", "window_size", "entropy", 0, 1, 2, 3, 4],
    )

    result = pf.to_dataframe()

    pd.testing.assert_frame_equal(result, expected)
