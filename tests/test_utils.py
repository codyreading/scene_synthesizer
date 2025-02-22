# Copyright (c) 2021-2024, NVIDIA CORPORATION & AFFILIATES.  All rights reserved.
#
# SPDX-License-Identifier: Apache-2.0

import pytest
import functools
from contextlib import contextmanager
import yourdfpy

from pxr.Tf import ErrorException

def _skip_if_file_is_missing(test_func):
    @functools.wraps(test_func)
    def wrapper(*args, **kwargs):
        try:
            return test_func(*args, **kwargs)
        except ValueError as e:
            if 'is not a file' in str(e):
                pytest.skip(f"Skipping {test_func.__name__}: {e}")
            raise
        except ImportError as e:
            pytest.skip(f"Skipping {test_func.__name__}: {e}")
        except Exception as e:  # Catch all exceptions instead of an undefined 'ErrorException'
            if 'Failed to open layer' in str(e):
                pytest.skip(f"Skipping {test_func.__name__}: {e}")
            raise
    return wrapper


@contextmanager
def yourdfpy_equality_tolerance(value):
    original_value = yourdfpy.urdf.EQUALITY_TOLERANCE
    yourdfpy.urdf.EQUALITY_TOLERANCE = value
    try:
        yield
    finally:
        yourdfpy.urdf.EQUALITY_TOLERANCE = original_value
