import numpy as np


class Image():
    """_summary_
    """

    def __init__(self, xsize, ysize, dtype=np.float64):

        self.xsize = xsize
        self.ysize = ysize
        self._dtype = dtype
        self._setup_image()

    def _setup_image(self):

        self.array = np.zeros((self.xsize, self.ysize), dtype=self._dtype)


class MaskedImageF():
    """_summary_
    """

    def __init__(self, *args):

        if len(args) == 1:
            if isinstance(args[0], int):
                self._xsize = args[0]
                self._ysize = args[0]
            elif isinstance(args[0], (MaskedImageF, ExposureF)):
                self._xsize = args[0]._xsize
                self._ysize = args[0]._ysize
            else:
                raise ValueError(
                    "Class must be instentiate with either an image size or an"
                    " already instentiate MaskedImageF or ExposureF."
                )
        elif len(args) == 2:
            if all(isinstance(x, int) for x in args):
                self._xsize = args[0]
                self._ysize = args[1]
            else:
                raise ValueError(
                    "You must provide both axis size as integer."
                )
        self._setup_all()

    def _setup_all(self):

        self.image = Image(self._xsize, self._ysize)
        self.variance = Image(self._xsize, self._ysize)
        self.mask = Image(self._xsize, self._ysize, dtype=np.int16)


class ExposureF():
    """_summary_
    """

    def __init__(self, *args):

        if len(args) == 1:
            if isinstance(args[0], int):
                self._xsize = args[0]
                self._ysize = args[0]
                self._setup_all()
            elif isinstance(args[0], MaskedImageF):
                self._xsize = args[0]._xsize
                self._ysize = args[0]._ysize
                self.mask = args[0].mask
                self.image = args[0].image
                self.variance = args[0].variance
            else:
                raise ValueError(
                    "Class must be instentiate with either an image size or an"
                    " already instentiate MaskedImageF or ExposureF."
                )
        elif len(args) == 2:
            if all(isinstance(x, int) for x in args):
                self._xsize = args[0]
                self._ysize = args[1]
                self._setup_all()
            else:
                raise ValueError(
                    "You must provide both axis size as integer."
                )

    @property
    def FilterLabel(self):
        return self._filter_label

    @property
    def psf(self):
        return self._psf

    @property
    def wcs(self):
        return self._wcs

    def setFilterLabel(self, filter_label):

        if isinstance(filter_label, FilterLabel):
            self._filter_label = filter_label
        else:
            raise ValueError(
                "filter_label must be a FilterLabel"
            )

    def setPsf(self, psf):
        self._psf = psf

    def setWcs(self, wcs):
        self._wcs = wcs

    def _setup_all(self):

        self.image = Image(self._xsize, self._ysize)
        # self.variance = Image(self._xsize, self._ysize)
        # self.mask = Image(self._xsize, self._ysize, dtype=np.int16)


class FilterLabel():

    def __init__(self, band, physical):

        self.band = band
        self.physical = physical
