# -*- coding: utf-8 -*-
# Copyright (c) 2020, Matgenix SRL


import os

import pandas as pd
import pytest
from monty.tempfile import ScratchDir

import pysisso
from pysisso.inputs import SISSODat, SISSOIn

TEST_FILES_DIR = os.path.abspath(
    os.path.join(pysisso.__file__, "..", "..", "test_files")
)


@pytest.mark.unit
def test_sisso_dat():
    sisso_dat = SISSODat.from_dat_file(
        filepath=os.path.join(TEST_FILES_DIR, "inputs", "train.dat_regression")
    )
    assert sisso_dat.nsample == 5
    assert sisso_dat.nsf == 3
    assert sisso_dat.ntask == 1
    assert isinstance(sisso_dat.data, pd.DataFrame)

    sisso_dat = SISSODat.from_file(
        filepath=os.path.join(
            TEST_FILES_DIR, "runs", "perfect_linear_5pts", "train.dat"
        )
    )
    assert sisso_dat.nsample == 5

    with pytest.raises(
        ValueError, match=r'Type "<class \'float\'>" ' r"is not valid for nsample."
    ):
        sisso_dat.nsample = 2.1

    with pytest.raises(
        ValueError, match=r"The size of the DataFrame does not " r"match nsample."
    ):
        sisso_dat.nsample = 4

    sisso_dat = SISSODat.from_dat_file(
        filepath=os.path.join(TEST_FILES_DIR, "inputs", "train.dat_regression"),
        features_dimensions={"feature1": "dim1", "feature3": "dim1"},
    )
    assert list(sisso_dat.data.columns) == [
        "materials",
        "property",
        "feature2",
        "feature1",
        "feature3",
    ]
    assert sisso_dat.SISSO_features_dimensions_ranges == {"dim1": (2, 3), None: (1, 1)}

    sisso_dat = SISSODat.from_dat_file(
        filepath=os.path.join(TEST_FILES_DIR, "inputs", "train.dat_regression"),
        features_dimensions={},
    )
    assert list(sisso_dat.data.columns) == [
        "materials",
        "property",
        "feature1",
        "feature2",
        "feature3",
    ]
    assert sisso_dat.SISSO_features_dimensions_ranges == {None: (1, 3)}

    with pytest.raises(ValueError, match=r""):
        SISSODat.from_dat_file(
            filepath=os.path.join(TEST_FILES_DIR, "inputs", "train.dat_regression"),
            features_dimensions={"feature1": "_NODIM"},
        )


@pytest.mark.unit
def test_sisso_in():
    sisso_dat = SISSODat.from_dat_file(
        filepath=os.path.join(TEST_FILES_DIR, "inputs", "train.dat_regression")
    )
    sisso_in = SISSOIn.from_SISSO_dat(sisso_dat=sisso_dat)
    assert sisso_in.is_regression is True
    with ScratchDir("."):
        sisso_in.to_file()
        assert os.path.exists("SISSO.in")
        with open("SISSO.in", "r") as f:
            content = f.read()
        assert "SISSO.in generated by Matgenix's pysisso package." in content
        assert "ntask=1\nnsample=5" in content
        assert "method='L0'\nL1L0_size4L0=1\nfit_intercept=.true." in content

    sisso_in = SISSOIn.from_sisso_keywords(
        ptype=1, method="L1L0", desc_dim=1, L1L0_size4L0=1
    )
    assert sisso_in.descriptor_identification_keywords["method"] == "L1L0"

    with pytest.raises(
        ValueError,
        match=r"Dimension of descriptor \(desc_dim=2\) is "
        r"larger than the number of features "
        r"available for L0 norm from L1 screening "
        r"\(L1L0_size4L0=1\).",
    ):
        SISSOIn.from_sisso_keywords(ptype=1, method="L1L0", desc_dim=2, L1L0_size4L0=1)

    sisso_in = SISSOIn.from_sisso_keywords(
        ptype=1, method="L1L0", desc_dim=4, L1L0_size4L0=2, fix=True
    )
    assert sisso_in.descriptor_identification_keywords["L1L0_size4L0"] == 4
    assert sisso_in.target_properties_keywords["desc_dim"] == 4

    with pytest.raises(
        ValueError,
        match=r"Number of features to be screened by L1 "
        r"for L0 \(L1L0_size4L0=4\) is larger "
        r"than SIS-selected subspace "
        r"\(subs_sis=2\).",
    ):
        SISSOIn.from_sisso_keywords(
            ptype=1, method="L1L0", desc_dim=1, L1L0_size4L0=4, subs_sis=2
        )
    sisso_in = SISSOIn.from_sisso_keywords(
        ptype=1, method="L1L0", desc_dim=1, L1L0_size4L0=4, subs_sis=2, fix=True
    )
    assert sisso_in.descriptor_identification_keywords["L1L0_size4L0"] == 4
    fcsis_kwds = sisso_in.feature_construction_sure_independence_screening_keywords
    assert fcsis_kwds["subs_sis"] == 4

    with pytest.raises(
        ValueError,
        match=r"Number of features to be screened by L1 "
        r"for L0 \(L1L0_size4L0=4\) is larger "
        r"than SIS-selected subspace \(subs_sis=2\) "
        r"of dimension 3.",
    ):
        SISSOIn.from_sisso_keywords(
            ptype=1, method="L1L0", desc_dim=1, L1L0_size4L0=4, subs_sis=[8, 4, 2, 3]
        )
    sisso_in = SISSOIn.from_sisso_keywords(
        ptype=1,
        method="L1L0",
        desc_dim=1,
        L1L0_size4L0=4,
        subs_sis=[8, 4, 2, 3],
        fix=True,
    )
    assert sisso_in.descriptor_identification_keywords["L1L0_size4L0"] == 4
    fcsis_kwds = sisso_in.feature_construction_sure_independence_screening_keywords
    assert fcsis_kwds["subs_sis"] == [8, 4, 4, 4]

    assert sisso_in.is_classification is False

    sisso_dat = SISSODat.from_dat_file(
        filepath=os.path.join(TEST_FILES_DIR, "inputs", "train.dat_regression"),
        features_dimensions={"feature1": "dim1", "feature3": "dim1"},
    )
    sisso_in = SISSOIn.from_SISSO_dat(sisso_dat=sisso_dat)
    fcsis_kwds = sisso_in.feature_construction_sure_independence_screening_keywords
    assert fcsis_kwds["dimclass"] == "(2:3)"

    sisso_dat = SISSODat.from_dat_file(
        filepath=os.path.join(TEST_FILES_DIR, "inputs", "train.dat_regression"),
        features_dimensions={},
    )
    sisso_in = SISSOIn.from_SISSO_dat(sisso_dat=sisso_dat)
    fcsis_kwds = sisso_in.feature_construction_sure_independence_screening_keywords
    assert fcsis_kwds["dimclass"] is None

    with pytest.raises(
        ValueError,
        match=r'Wrong model_type \("wrong_model_type"\). '
        r'Should be "regression" or '
        r'"classification".',
    ):
        SISSOIn.from_SISSO_dat(sisso_dat=sisso_dat, model_type="wrong_model_type")

    sisso_in = SISSOIn.from_SISSO_dat(sisso_dat=sisso_dat, task_weighting=None)
    sisso_string = sisso_in.input_string
    assert "task_weighting" not in sisso_string
    assert "! REGRESSION MODEL !" in sisso_string
