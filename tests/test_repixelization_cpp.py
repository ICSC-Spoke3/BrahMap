import pytest
import numpy as np
import repixelize

import helper_ComputeWeights as cw
import helper_Repixelization as rp


class InitCommonParams:
    np.random.seed(1234)
    npix = 128
    nsamples = npix * 10

    pointings_flag = np.ones(nsamples, dtype=bool)
    bad_samples = np.random.randint(low=0, high=nsamples, size=100)
    pointings_flag[bad_samples] = False


class InitInt32Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.int32
        self.pointings = np.random.randint(
            low=0, high=self.npix, size=self.nsamples, dtype=self.dtype
        )


class InitInt64Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.int64
        self.pointings = np.random.randint(
            low=0, high=self.npix, size=self.nsamples, dtype=self.dtype
        )


class InitFloat32Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.float32
        self.noise_weights = np.random.random(size=self.nsamples).astype(
            dtype=self.dtype
        )
        self.pol_angles = np.random.uniform(
            low=-np.pi / 2.0, high=np.pi / 2.0, size=self.nsamples
        ).astype(dtype=self.dtype)


class InitFloat64Params(InitCommonParams):
    def __init__(self) -> None:
        super().__init__()

        self.dtype = np.float64
        self.noise_weights = np.random.random(size=self.nsamples).astype(
            dtype=self.dtype
        )
        self.pol_angles = np.random.uniform(
            low=-np.pi / 2.0, high=np.pi / 2.0, size=self.nsamples
        ).astype(dtype=self.dtype)


@pytest.mark.parametrize(
    "initint, initfloat, rtol",
    [
        (InitInt32Params(), InitFloat32Params(), 1.5e-4),
        (InitInt64Params(), InitFloat32Params(), 1.5e-4),
        (InitInt32Params(), InitFloat64Params(), 1.5e-5),
        (InitInt64Params(), InitFloat64Params(), 1.5e-5),
    ],
)
class TestRepixelization(InitCommonParams):
    def test_repixelize_pol_I(self, initint, initfloat, rtol):
        new_npix, py_weighted_counts, pixel_mask = cw.computeweights_pol_I(
            self.npix,
            self.nsamples,
            initint.pointings,
            self.pointings_flag,
            initfloat.noise_weights,
            dtype_float=initfloat.dtype,
        )

        cpp_weighted_counts = py_weighted_counts.copy()

        repixelize.repixelize_pol_I(new_npix, pixel_mask, cpp_weighted_counts)

        cpp_weighted_counts.resize(new_npix, refcheck=False)

        py_weighted_counts = rp.repixelize_pol_I(
            new_npix, pixel_mask, py_weighted_counts
        )

        np.testing.assert_allclose(py_weighted_counts, cpp_weighted_counts, rtol=rtol)

    def test_repixelize_pol_QU(self, initint, initfloat, rtol):
        (
            py_weighted_counts,
            __,
            __,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
        ) = cw.computeweights_pol_QU(
            self.npix,
            self.nsamples,
            initint.pointings,
            self.pointings_flag,
            initfloat.noise_weights,
            initfloat.pol_angles,
            dtype_float=initfloat.dtype,
        )

        new_npix, pixel_mask = cw.get_pix_mask_pol(
            2,
            1.0e3,
            py_weighted_counts,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
        )

        cpp_weighted_counts = py_weighted_counts.copy()
        cpp_weighted_sin_sq = py_weighted_sin_sq.copy()
        cpp_weighted_cos_sq = py_weighted_cos_sq.copy()
        cpp_weighted_sincos = py_weighted_sincos.copy()

        repixelize.repixelize_pol_QU(
            new_npix,
            pixel_mask,
            cpp_weighted_counts,
            cpp_weighted_sin_sq,
            cpp_weighted_cos_sq,
            cpp_weighted_sincos,
        )

        cpp_weighted_counts.resize(new_npix, refcheck=False)
        cpp_weighted_sin_sq.resize(new_npix, refcheck=False)
        cpp_weighted_cos_sq.resize(new_npix, refcheck=False)
        cpp_weighted_sincos.resize(new_npix, refcheck=False)

        (
            py_weighted_counts,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
        ) = rp.repixelize_pol_QU(
            new_npix,
            pixel_mask,
            py_weighted_counts,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
        )

        np.testing.assert_allclose(py_weighted_counts, cpp_weighted_counts, rtol=rtol)
        np.testing.assert_allclose(py_weighted_sin_sq, cpp_weighted_sin_sq, rtol=rtol)
        np.testing.assert_allclose(py_weighted_cos_sq, cpp_weighted_cos_sq, rtol=rtol)
        np.testing.assert_allclose(py_weighted_sincos, cpp_weighted_sincos, rtol=rtol)

    def test_repixelize_pol_IQU(self, initint, initfloat, rtol):
        (
            py_weighted_counts,
            __,
            __,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
            py_weighted_sin,
            py_weighted_cos,
        ) = cw.computeweights_pol_IQU(
            self.npix,
            self.nsamples,
            initint.pointings,
            self.pointings_flag,
            initfloat.noise_weights,
            initfloat.pol_angles,
            dtype_float=initfloat.dtype,
        )

        new_npix, pixel_mask = cw.get_pix_mask_pol(
            3,
            1.0e3,
            py_weighted_counts,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
        )

        cpp_weighted_counts = py_weighted_counts.copy()
        cpp_weighted_sin_sq = py_weighted_sin_sq.copy()
        cpp_weighted_cos_sq = py_weighted_cos_sq.copy()
        cpp_weighted_sincos = py_weighted_sincos.copy()
        cpp_weighted_sin = py_weighted_sin.copy()
        cpp_weighted_cos = py_weighted_cos.copy()

        repixelize.repixelize_pol_IQU(
            new_npix,
            pixel_mask,
            cpp_weighted_counts,
            cpp_weighted_sin_sq,
            cpp_weighted_cos_sq,
            cpp_weighted_sincos,
            cpp_weighted_sin,
            cpp_weighted_cos,
        )

        cpp_weighted_counts.resize(new_npix, refcheck=False)
        cpp_weighted_sin_sq.resize(new_npix, refcheck=False)
        cpp_weighted_cos_sq.resize(new_npix, refcheck=False)
        cpp_weighted_sincos.resize(new_npix, refcheck=False)
        cpp_weighted_sin.resize(new_npix, refcheck=False)
        cpp_weighted_cos.resize(new_npix, refcheck=False)

        (
            py_weighted_counts,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
            py_weighted_sin,
            py_weighted_cos,
        ) = rp.repixelize_pol_IQU(
            new_npix,
            pixel_mask,
            py_weighted_counts,
            py_weighted_sin_sq,
            py_weighted_cos_sq,
            py_weighted_sincos,
            py_weighted_sin,
            py_weighted_cos,
        )

        np.testing.assert_allclose(py_weighted_counts, cpp_weighted_counts, rtol=rtol)
        np.testing.assert_allclose(py_weighted_sin_sq, cpp_weighted_sin_sq, rtol=rtol)
        np.testing.assert_allclose(py_weighted_cos_sq, cpp_weighted_cos_sq, rtol=rtol)
        np.testing.assert_allclose(py_weighted_sincos, cpp_weighted_sincos, rtol=rtol)
        np.testing.assert_allclose(py_weighted_sin, cpp_weighted_sin, rtol=rtol)
        np.testing.assert_allclose(py_weighted_cos, cpp_weighted_cos, rtol=rtol)


if __name__ == "__main__":
    pytest.main([f"{__file__}::TestRepixelization::test_repixelize_pol_I", "-v", "-s"])
    pytest.main([f"{__file__}::TestRepixelization::test_repixelize_pol_QU", "-v", "-s"])
    pytest.main(
        [f"{__file__}::TestRepixelization::test_repixelize_pol_IQU", "-v", "-s"]
    )
