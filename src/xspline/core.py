# -*- coding: utf-8 -*-
"""
    core
    ~~~~

    core module contains main functions and classes.
"""
import numpy as np
from . import utils


def bspline_domain(knots, degree, idx, l_extra=False, r_extra=False):
    r"""Compute the support for the spline basis, knots degree and the index of
    the basis.

    Args:
        knots (numpy.ndarray):
        1D array that stores the knots of the splines.

        degree (int):
        A non-negative integer that indicates the degree of the polynomial.

        idx (int):
        A non-negative integer that indicates the index in the spline bases
        list.

        l_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at left end.
        Default to be False.

        r_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at right end.
        Default to be False.

    Returns:
        numpy.ndarray:
        1D array with two elements represents that left and right end of the
        support of the spline basis.
    """
    num_knots = knots.size
    num_intervals = num_knots - 1
    num_splines = num_intervals + degree

    if idx == -1:
        idx = num_splines - 1

    lb = knots[max(idx - degree, 0)]
    ub = knots[min(idx + 1, num_intervals)]

    if idx == 0 and l_extra:
        lb = -np.inf
    if idx == num_splines - 1 and r_extra:
        ub = np.inf

    return np.array([lb, ub])


def bspline_fun(x, knots, degree, idx, l_extra=False, r_extra=False):
    r"""Compute the spline basis.

    Args:
        x (float | numpy.ndarray):
        Scalar or numpy array that store the independent variables.

        knots (numpy.ndarray):
        1D array that stores the knots of the splines.

        degree (int):
        A non-negative integer that indicates the degree of the polynomial.

        idx (int):
        A non-negative integer that indicates the index in the spline bases
        list.

        l_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at left end.
        Default to be False.

        r_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at right end.
        Default to be False.

    Returns:
        float | numpy.ndarray:
        Function values of the corresponding spline bases.
    """
    num_knots = knots.size
    num_intervals = num_knots - 1
    num_splines = num_intervals + degree

    if idx == -1:
        idx = num_splines - 1

    b = bspline_domain(knots, degree, idx, l_extra=l_extra, r_extra=r_extra)

    if degree == 0:
        f = utils.indicator_f(x, b, r_close=(idx == num_splines - 1))
        return f

    if idx == 0:
        b_effect = bspline_domain(knots, degree, idx)
        y = utils.indicator_f(x, b)
        z = utils.linear_rf(x, b_effect)
        return y*(z**degree)

    if idx == num_splines - 1:
        b_effect = bspline_domain(knots, degree, idx)
        y = utils.indicator_f(x, b, r_close=True)
        z = utils.linear_lf(x, b_effect)
        return y*(z**degree)

    lf = bspline_fun(x, knots, degree - 1, idx - 1,
                     l_extra=l_extra, r_extra=r_extra)
    lf *= utils.linear_lf(x, bspline_domain(knots, degree - 1, idx - 1))

    rf = bspline_fun(x, knots, degree - 1, idx,
                     l_extra=l_extra, r_extra=r_extra)
    rf *= utils.linear_rf(x, bspline_domain(knots, degree - 1, idx))

    return lf + rf


def bspline_dfun(x, knots, degree, order, idx, l_extra=False, r_extra=False):
    r"""Compute the derivative of the spline basis.

    Args:
        x (float | numpy.ndarray):
        Scalar or numpy array that store the independent variables.

        knots (numpy.ndarray):
        1D array that stores the knots of the splines.

        degree (int):
        A non-negative integer that indicates the degree of the polynomial.

        order (int):
        A non-negative integer that indicates the order of differentiation.

        idx (int):
        A non-negative integer that indicates the index in the spline bases
        list.

        l_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at left end.
        Default to be False.

        r_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at right end.
        Default to be False.

    Returns:
        float | numpy.ndarray:
        Derivative values of the corresponding spline bases.
    """
    num_knots = knots.size
    num_intervals = num_knots - 1
    num_splines = num_intervals + degree

    if idx == -1:
        idx = num_splines - 1

    if order == 0:
        return bspline_fun(x, knots, degree, idx,
                           l_extra=l_extra, r_extra=r_extra)

    if order > degree:
        return np.zeros(x.size)

    if idx == 0:
        rdf = 0.0
    else:
        b = bspline_domain(knots, degree - 1, idx - 1)
        d = b[1] - b[0]
        f = (x - b[0])/d
        rdf = f*bspline_dfun(x, knots, degree - 1, order, idx - 1,
                             l_extra=l_extra, r_extra=r_extra)
        rdf += order*bspline_dfun(x, knots, degree - 1, order - 1, idx - 1,
                                  l_extra=l_extra, r_extra=r_extra)/d

    if idx == num_splines - 1:
        ldf = 0.0
    else:
        b = bspline_domain(knots, degree - 1, idx)
        d = b[0] - b[1]
        f = (x - b[1])/d
        ldf = f*bspline_dfun(x, knots, degree - 1, order, idx,
                             l_extra=l_extra, r_extra=r_extra)
        ldf += order*bspline_dfun(x, knots, degree - 1, order - 1, idx,
                                  l_extra=l_extra, r_extra=r_extra)/d

    return ldf + rdf


def bspline_ifun(a, x, knots, degree, order, idx, l_extra=False, r_extra=False):
    r"""Compute the integral of the spline basis.

    Args:
        a (float | numpy.ndarray):
        Scalar or numpy array that store the starting point of the integration.

        x (float | numpy.ndarray):
        Scalar or numpy array that store the ending point of the integration.

        knots (numpy.ndarray):
        1D array that stores the knots of the splines.

        degree (int):
        A non-negative integer that indicates the degree of the polynomial.

        order (int):
        A non-negative integer that indicates the order of integration.

        idx (int):
        A non-negative integer that indicates the index in the spline bases
        list.

        l_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at left end.
        Default to be False.

        r_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at right end.
        Default to be False.

    Returns:
        float | numpy.ndarray:
        Integral values of the corresponding spline bases.
    """
    num_knots = knots.size
    num_intervals = num_knots - 1
    num_splines = num_intervals + degree

    if idx == -1:
        idx = num_splines - 1

    if order == 0:
        return bspline_fun(x, knots, degree, idx,
                           l_extra=l_extra, r_extra=r_extra)

    if degree == 0:
        b = bspline_domain(knots, degree, idx, l_extra=l_extra, r_extra=r_extra)
        return utils.indicator_if(a, x, order, b)

    if idx == 0:
        rif = 0.0
    else:
        b = bspline_domain(knots, degree - 1, idx - 1)
        d = b[1] - b[0]
        f = (x - b[0]) / d
        rif = f*bspline_ifun(a, x, knots, degree - 1, order, idx - 1,
                             l_extra=l_extra, r_extra=r_extra)
        rif -= order*bspline_ifun(a, x, knots, degree - 1, order + 1, idx - 1,
                                  l_extra=l_extra, r_extra=r_extra)/d

    if idx == num_splines - 1:
        lif = 0.0
    else:
        b = bspline_domain(knots, degree - 1, idx)
        d = b[0] - b[1]
        f = (x - b[1]) / d
        lif = f*bspline_ifun(a, x, knots, degree - 1, order, idx,
                             l_extra=l_extra, r_extra=r_extra)
        lif -= order*bspline_ifun(a, x, knots, degree - 1, order + 1, idx,
                                  l_extra=l_extra, r_extra=r_extra)/d

    return lif + rif


class XSpline:
    """XSpline main class of the package.
    """
    def __init__(self, knots, degree, l_linear=False, r_linear=False):
        r"""Constructor of the XSpline class.

        knots (numpy.ndarray):
        1D numpy array that store the knots, must including that boundary knots.

        degree (int):
        A non-negative integer that indicates the degree of the spline.

        l_linear (bool, optional):
        A bool variable, that if using the linear tail at left end.

        r_linear (bool, optional):
        A bool variable, that if using the linear tail at right end.
        """
        # pre-process the knots vector
        knots = list(set(knots))
        knots = np.sort(np.array(knots))

        self.knots = knots
        self.degree = degree
        self.l_linear = l_linear
        self.r_linear = r_linear

        # dimensions
        self.num_knots = knots.size
        self.num_intervals = knots.size - 1
        self.num_spline_bases = self.num_intervals + self.degree

        # check inputs
        int_l_linear = int(l_linear)
        int_r_linear = int(r_linear)
        assert self.num_intervals >= 1 + int_l_linear + int_r_linear
        assert isinstance(self.degree, int) and self.degree >= 0

        # create inner knots
        self.inner_knots = self.knots[int_l_linear:
                                      self.num_knots - int_r_linear]
        self.lb = self.knots[0]
        self.ub = self.knots[-1]
        self.inner_lb = self.inner_knots[0]
        self.inner_ub = self.inner_knots[-1]

    def domain(self, idx, l_extra=False, r_extra=False):
        """Return the support of the XSpline.

        idx (int):
        A non-negative integer that indicates the index in the spline bases
        list.

        l_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at left end.
        Default to be False.

        r_extra (bool, optional):
        A optional bool variable indicates that if extrapolate at right end.
        Default to be False.

        Returns:
            numpy.ndarray:
            1D array with two elements represents that left and right end of the
            support of the spline basis.
        """
        inner_domain = bspline_domain(self.inner_knots,
                                      self.degree,
                                      idx,
                                      l_extra=l_extra,
                                      r_extra=r_extra)
        lb = inner_domain[0]
        ub = inner_domain[1]

        lb = self.lb if inner_domain[0] == self.inner_lb else lb
        ub = self.ub if inner_domain[1] == self.inner_ub else ub

        return np.array([lb, ub])

    def fun(self, x, idx, l_extra=False, r_extra=False):
        r"""Compute the spline basis.

        Args:
            x (float | numpy.ndarray):
            Scalar or numpy array that store the independent variables.

            idx (int):
            A non-negative integer that indicates the index in the spline bases
            list.

            l_extra (bool, optional):
            A optional bool variable indicates that if extrapolate at left end.
            Default to be False.

            r_extra (bool, optional):
            A optional bool variable indicates that if extrapolate at right end.
            Default to be False.

        Returns:
            float | numpy.ndarray:
            Function values of the corresponding spline bases.
        """
        if not self.l_linear and not self.r_linear:
            return bspline_fun(x,
                               self.inner_knots,
                               self.degree,
                               idx,
                               l_extra=l_extra,
                               r_extra=r_extra)

        x_is_scalar = np.isscalar(x)
        if x_is_scalar:
            x = np.array([x])

        f = np.zeros(x.size)
        m_idx = np.array([True] * x.size)

        if self.l_linear:
            l_idx = (x < self.inner_lb) & ((x >= self.lb) | l_extra)
            m_idx &= (x >= self.inner_lb)

            inner_lb_fun = bspline_fun(self.inner_lb,
                                       self.inner_knots,
                                       self.degree,
                                       idx)
            inner_lb_dfun = bspline_dfun(self.inner_lb,
                                         self.inner_knots,
                                         self.degree,
                                         1, idx)

            f[l_idx] = inner_lb_fun + inner_lb_dfun * (x[l_idx] - self.inner_lb)

        if self.r_linear:
            u_idx = (x > self.inner_ub) & ((x <= self.ub) | r_extra)
            m_idx &= (x <= self.inner_ub)

            inner_ub_fun = bspline_fun(self.inner_ub,
                                       self.inner_knots,
                                       self.degree,
                                       idx)
            inner_ub_dfun = bspline_dfun(self.inner_ub,
                                         self.inner_knots,
                                         self.degree,
                                         1, idx)

            f[u_idx] = inner_ub_fun + inner_ub_dfun * (x[u_idx] - self.inner_ub)

        f[m_idx] = bspline_fun(x[m_idx],
                               self.inner_knots,
                               self.degree,
                               idx,
                               l_extra=l_extra,
                               r_extra=r_extra)

        if x_is_scalar:
            return f[0]
        else:
            return f

# TODO:
# 1. bspline function pass in too many default every time
# 2. name of f, df and if
# 3. the way to deal with the scalar vs array.
# test these two functions first next time and then modify correspondingly.
