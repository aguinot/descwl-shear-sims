import os
import pytest
import numpy as np
from ..se_obs import SEObs
from ..sim import (
    make_sim,
    make_galaxy_catalog,
    StarCatalog,
    make_psf,
    make_ps_psf,
    get_se_dim,
)
from ..sim.constants import ZERO_POINT

from ..sim.galaxy_catalogs import DEFAULT_FIXED_GAL_CONFIG


@pytest.mark.parametrize('dither,rotate', [
    (False, False),
    (False, True),
    (True, False),
    (True, True),
])
def test_sim_smoke(dither, rotate):
    """
    test sim can run
    """
    seed = 74321
    rng = np.random.RandomState(seed)

    coadd_dim = 341
    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="exp",
        coadd_dim=coadd_dim,
        buff=30,
        layout="grid",
    )

    psf = make_psf(psf_type="gauss")
    data = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=351,
        g1=0.02,
        g2=0.00,
        psf=psf,
        dither=dither,
        rotate=rotate,
    )

    for band, bdata in data['band_data'].items():
        assert len(bdata) == 1
        assert isinstance(bdata[0], SEObs)


def test_sim():

    bands = ["i"]
    seed = 7421
    coadd_dim = 201
    psf_dim = 47
    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="exp",
        coadd_dim=coadd_dim,
        buff=30,
        layout="grid",
    )

    psf = make_psf(psf_type="moffat")
    sim_data = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=coadd_dim,
        psf_dim=psf_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
        bands=bands,
    )

    assert 'coadd_dims' in sim_data
    assert sim_data['coadd_dims'] == [coadd_dim]*2
    assert 'psf_dims' in sim_data
    assert sim_data['psf_dims'] == [psf_dim]*2

    band_data = sim_data['band_data']
    assert len(band_data) == len(bands)
    for band in bands:
        assert band in band_data


@pytest.mark.parametrize("rotate", [False, True])
def test_sim_exp_mag(rotate):
    """
    test we get the right mag.  Also test we get small flux when we rotate and
    there is nothing at the sub image location we choose
    """

    bands = ["i"]
    seed = 8123
    coadd_dim = 301
    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="exp",
        coadd_dim=coadd_dim,
        buff=30,
        layout="grid",
    )

    psf = make_psf(psf_type="gauss")
    sim_data = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=coadd_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
        bands=bands,
        rotate=rotate,
    )

    image = sim_data["band_data"]["i"][0].image.array
    subim_sum = image[105:130, 100:125].sum()

    if rotate:
        # we expect nothing there
        assert abs(subim_sum) < 30
    else:
        # we expect something there with about the right magnitude
        mag = ZERO_POINT - 2.5*np.log10(subim_sum)
        assert abs(mag - DEFAULT_FIXED_GAL_CONFIG['mag']) < 0.005


@pytest.mark.parametrize("psf_type", ["gauss", "moffat", "ps"])
def test_sim_psf_type(psf_type):

    seed = 431
    rng = np.random.RandomState(seed)

    coadd_dim = 101
    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="exp",
        coadd_dim=coadd_dim,
        buff=5,
        layout="grid",
    )

    if psf_type == "ps":
        se_dim = get_se_dim(coadd_dim=coadd_dim)
        psf = make_ps_psf(rng=rng, dim=se_dim)
    else:
        psf = make_psf(psf_type=psf_type)

    _ = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=coadd_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
        dither=True,
        rotate=True,
    )


@pytest.mark.parametrize('epochs_per_band', [1, 2, 3])
def test_sim_epochs(epochs_per_band):

    seed = 7421
    bands = ["r", "i", "z"]
    coadd_dim = 301
    psf_dim = 47

    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="exp",
        coadd_dim=coadd_dim,
        buff=10,
        layout="grid",
    )

    psf = make_psf(psf_type="gauss")
    sim_data = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=coadd_dim,
        psf_dim=psf_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
        bands=bands,
        epochs_per_band=epochs_per_band,
    )

    band_data = sim_data['band_data']
    for band in bands:
        assert band in band_data
        assert len(band_data[band]) == epochs_per_band


@pytest.mark.parametrize("layout", ("grid", "random"))
def test_sim_layout(layout):
    seed = 7421
    coadd_dim = 201
    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="exp",
        coadd_dim=coadd_dim,
        buff=30,
        layout=layout,
    )

    psf = make_psf(psf_type="gauss")
    _ = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=coadd_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
    )


@pytest.mark.parametrize(
    "cosmic_rays, bad_columns",
    [(True, True),
     (True, False),
     (False, True),
     (True, True)],
)
def test_sim_defects(cosmic_rays, bad_columns):
    seed = 7421
    coadd_dim = 201
    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="exp",
        coadd_dim=coadd_dim,
        layout="grid",
        buff=30,
    )

    psf = make_psf(psf_type="gauss")
    _ = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=coadd_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
        cosmic_rays=cosmic_rays,
        bad_columns=bad_columns,
    )


@pytest.mark.skipif(
    "CATSIM_DIR" not in os.environ,
    reason='simulation input data is not present',
)
def test_sim_wldeblend():
    seed = 7421
    coadd_dim = 201
    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="wldeblend",
        coadd_dim=coadd_dim,
        buff=30,
    )

    psf = make_psf(psf_type="moffat")
    _ = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        coadd_dim=coadd_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
    )


@pytest.mark.skipif(
    "CATSIM_DIR" not in os.environ,
    reason='simulation input data is not present',
)
def test_sim_stars():
    seed = 7421
    coadd_dim = 201
    buff = 30
    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="wldeblend",
        coadd_dim=coadd_dim,
        buff=buff,
    )

    star_catalog = StarCatalog(
        rng=rng,
        coadd_dim=coadd_dim,
        buff=buff,
        density=100,
    )

    psf = make_psf(psf_type="moffat")
    _ = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        star_catalog=star_catalog,
        coadd_dim=coadd_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
    )


@pytest.mark.skipif(
    "CATSIM_DIR" not in os.environ,
    reason='simulation input data is not present',
)
def test_sim_star_bleeds():
    seed = 7421
    coadd_dim = 201
    buff = 30
    rng = np.random.RandomState(seed)

    galaxy_catalog = make_galaxy_catalog(
        rng=rng,
        gal_type="wldeblend",
        coadd_dim=coadd_dim,
        buff=buff,
    )

    star_catalog = StarCatalog(
        rng=rng,
        coadd_dim=coadd_dim,
        buff=buff,
        density=100,
    )

    psf = make_psf(psf_type="moffat")
    _ = make_sim(
        rng=rng,
        galaxy_catalog=galaxy_catalog,
        star_catalog=star_catalog,
        coadd_dim=coadd_dim,
        g1=0.02,
        g2=0.00,
        psf=psf,
        star_bleeds=True,
    )