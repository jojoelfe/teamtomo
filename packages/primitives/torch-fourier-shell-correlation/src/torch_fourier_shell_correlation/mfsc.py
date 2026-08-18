"""Modified Fourier shell correlation (mFSC) from Penczek 2020."""

import torch
from torch_grid_utils import fftfreq_grid


def _modified_fourier_correlation(
    a: torch.Tensor,
    b: torch.Tensor,
    mask: torch.Tensor,
    sigma_pixels: float,
    ndim: int,
) -> torch.Tensor:
    """Compute modified Fourier correlation for arbitrary dimensionality.

    Core implementation shared by 2D (ring) and 3D (shell) variants.

    Parameters
    ----------
    a : torch.Tensor
        Input tensor of shape (..., *spatial_dims).
    b : torch.Tensor
        Input tensor of shape (..., *spatial_dims).
    mask : torch.Tensor
        Real-space mask broadcastable with input spatial dimensions.
    sigma_pixels : float
        Gaussian window sigma in Fourier pixels.
    ndim : int
        Number of spatial dimensions (2 or 3).

    Returns
    -------
    torch.Tensor
        Correlation values of shape (..., n_shells).
    """
    spatial_shape = a.shape[-ndim:]
    batch_shape = a.shape[:-ndim]
    device = a.device
    spatial_dims = tuple(range(-ndim, 0))

    # Number of shells matches existing FSC API
    n_shells = min(spatial_shape) // 2 + 1

    # Frequency radius grid in Fourier pixels
    frequency_grid = fftfreq_grid(
        image_shape=spatial_shape,
        rfft=False,
        fftshift=False,
        norm=True,
        device=device,
    )
    radius_pixels = frequency_grid * min(spatial_shape)

    # Compute full complex FFT once
    U = torch.fft.fftn(a, dim=spatial_dims)
    V = torch.fft.fftn(b, dim=spatial_dims)

    # Number of voxels in mask (for zero-mean subtraction)
    n_voxels = mask.sum(dim=spatial_dims, keepdim=True)

    # Loop over shells
    mfsc_results = []
    for s in range(n_shells):
        if s == 0:
            # DC component always 1.0
            mfsc_results.append(torch.ones(batch_shape, device=device))
        else:
            # Gaussian bandpass window centered at shell s
            W = torch.exp(-0.5 * ((radius_pixels - s) / sigma_pixels) ** 2)

            # Bandpass filter in Fourier space, inverse FFT to real space
            u_bp = torch.fft.ifftn(U * W, dim=spatial_dims).real
            v_bp = torch.fft.ifftn(V * W, dim=spatial_dims).real

            # Apply real-space mask
            u_masked = u_bp * mask
            v_masked = v_bp * mask

            # Zero-mean subtraction within mask
            u_mean = u_masked.sum(dim=spatial_dims, keepdim=True) / n_voxels
            v_mean = v_masked.sum(dim=spatial_dims, keepdim=True) / n_voxels
            u_masked = u_masked - u_mean * mask
            v_masked = v_masked - v_mean * mask

            # Pearson correlation coefficient
            num = torch.sum(u_masked * v_masked, dim=spatial_dims)
            u_var = torch.sum(u_masked**2, dim=spatial_dims)
            v_var = torch.sum(v_masked**2, dim=spatial_dims)
            den = torch.sqrt(u_var * v_var)

            corr = torch.where(den > 0, num / den, torch.zeros_like(num))
            mfsc_results.append(corr)

    return torch.stack(mfsc_results, dim=-1)


def modified_fourier_ring_correlation(
    a: torch.Tensor,
    b: torch.Tensor,
    mask: torch.Tensor,
    sigma_pixels: float = 1.0,
) -> torch.Tensor:
    """Modified Fourier ring correlation for 2D images with batching.

    Implements mFSC from Penczek 2020 (Eq 6): bandpass filter in Fourier space
    with Gaussian window, inverse FFT to real space, then apply real-space mask
    and correlate. This eliminates mask-induced cross-shell artifacts.

    Parameters
    ----------
    a : torch.Tensor
        Input tensor of shape ``(..., h, w)``.
    b : torch.Tensor
        Input tensor of shape ``(..., h, w)``.
    mask : torch.Tensor
        Real-space mask of shape ``(h, w)`` or ``(..., h, w)``. Must be
        broadcastable with input tensors.
    sigma_pixels : float, optional
        Gaussian window sigma in Fourier pixels (default: 1.0, per paper
        recommendation).

    Returns
    -------
    torch.Tensor
        Modified Fourier ring correlation values of shape
        ``(broadcast(...), min(h, w) // 2 + 1)``.

    Notes
    -----
    Unlike standard FSC which applies mask before FFT, mFSC applies bandpass
    filtering first in Fourier space, then masks in real space. This prevents
    the mask from introducing spurious correlations between frequency shells.

    References
    ----------
    Penczek, P.A. (2020). Reliable cryo-EM resolution estimation with modified
    Fourier shell correlation. IUCrJ, 7, 995-1008.
    """
    if a.ndim < 2:
        raise ValueError("Input tensors must have at least 2 dimensions.")
    if b.ndim < 2:
        raise ValueError("Input tensors must have at least 2 dimensions.")
    if a.shape[-2:] != b.shape[-2:]:
        raise ValueError(
            f"Spatial dimensions must match: a.shape[-2:] = {a.shape[-2:]} "
            f"vs b.shape[-2:] = {b.shape[-2:]}"
        )
    return _modified_fourier_correlation(a, b, mask, sigma_pixels, ndim=2)


def modified_fourier_shell_correlation(
    a: torch.Tensor,
    b: torch.Tensor,
    mask: torch.Tensor,
    sigma_pixels: float = 1.0,
) -> torch.Tensor:
    """Modified Fourier shell correlation for 3D volumes with batching.

    Implements mFSC from Penczek 2020 (Eq 6): bandpass filter in Fourier space
    with Gaussian window, inverse FFT to real space, then apply real-space mask
    and correlate. This eliminates mask-induced cross-shell artifacts.

    Parameters
    ----------
    a : torch.Tensor
        Input tensor of shape ``(..., d, h, w)``.
    b : torch.Tensor
        Input tensor of shape ``(..., d, h, w)``.
    mask : torch.Tensor
        Real-space mask of shape ``(d, h, w)`` or ``(..., d, h, w)``. Must be
        broadcastable with input tensors.
    sigma_pixels : float, optional
        Gaussian window sigma in Fourier pixels (default: 1.0, per paper
        recommendation).

    Returns
    -------
    torch.Tensor
        Modified Fourier shell correlation values of shape
        ``(broadcast(...), min(d, h, w) // 2 + 1)``.

    Notes
    -----
    Unlike standard FSC which applies mask before FFT, mFSC applies bandpass
    filtering first in Fourier space, then masks in real space. This prevents
    the mask from introducing spurious correlations between frequency shells.

    References
    ----------
    Penczek, P.A. (2020). Reliable cryo-EM resolution estimation with modified
    Fourier shell correlation. IUCrJ, 7, 995-1008.
    """
    if a.ndim < 3:
        raise ValueError("Input tensors must have at least 3 dimensions.")
    if b.ndim < 3:
        raise ValueError("Input tensors must have at least 3 dimensions.")
    if a.shape[-3:] != b.shape[-3:]:
        raise ValueError(
            f"Spatial dimensions must match: a.shape[-3:] = {a.shape[-3:]} "
            f"vs b.shape[-3:] = {b.shape[-3:]}"
        )
    return _modified_fourier_correlation(a, b, mask, sigma_pixels, ndim=3)
