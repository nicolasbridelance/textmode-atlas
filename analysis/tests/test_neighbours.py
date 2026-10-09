# SPDX-FileCopyrightText: 2026 textmode-atlas contributors
# SPDX-License-Identifier: Apache-2.0
import numpy as np
import pytest
from tm_analysis.neighbours import COLOURS, PROFILE, nearest, profile


def test_a_work_is_never_its_own_neighbour_and_ties_go_to_the_lower_index() -> None:
    matrix = np.array([[0.0], [1.0], [1.0], [3.0]])
    indexes, distances = nearest(matrix, 2)
    assert indexes.tolist() == [[1, 2], [2, 0], [1, 0], [1, 2]]
    assert distances[0].tolist() == [1.0, 1.0]


def test_k_is_capped_by_the_number_of_other_works() -> None:
    indexes, _ = nearest(np.zeros((3, 2)), 10)
    assert indexes.shape == (3, 2)


def test_the_profile_is_standardized_and_colours_are_shares() -> None:
    measures = [[float(i)] * len(PROFILE) for i in range(4)]
    colours = [[1.0] * COLOURS, [2.0] * COLOURS, [0.0] * COLOURS, [5.0] * COLOURS]
    matrix = profile(measures, colours)
    assert matrix.shape == (4, len(PROFILE) + COLOURS)
    assert np.allclose(matrix[:, 0].mean(), 0)
    assert np.allclose(matrix[:, 0].std(), 1)


def test_a_profile_of_the_wrong_shape_is_refused() -> None:
    with pytest.raises(ValueError, match="measures"):
        profile([[1.0]], [[1.0] * COLOURS])
