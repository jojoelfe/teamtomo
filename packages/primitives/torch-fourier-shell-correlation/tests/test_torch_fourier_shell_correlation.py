import pytest
import torch

from torch_fourier_shell_correlation import (
    fourier_ring_correlation,
    fourier_shell_correlation,
    modified_fourier_ring_correlation,
    modified_fourier_shell_correlation,
)


def test_fourier_ring_correlation_2d():
    """Test 2D fourier ring correlation without batching."""
    a = torch.zeros((10, 10))
    a[4:6, 4:6] = 1

    b = a
    result = fourier_ring_correlation(a, b)
    assert torch.allclose(result, torch.ones(6))

    b = torch.rand((10, 10))
    result = fourier_ring_correlation(a, b)
    assert not torch.allclose(result, torch.ones(6))


def test_fourier_shell_correlation_3d():
    """Test 3D fourier shell correlation without batching."""
    a = torch.zeros((10, 10, 10))
    a[4:6, 4:6, 4:6] = 1

    b = a
    result = fourier_shell_correlation(a, b)
    assert torch.allclose(result, torch.ones(6))

    b = torch.rand((10, 10, 10))
    result = fourier_shell_correlation(a, b)
    assert not torch.allclose(result, torch.ones(6))


def test_fourier_ring_correlation_batched():
    """Test 2D fourier ring correlation with batching."""
    # Single batch
    a = torch.zeros((2, 10, 10))
    a[:, 4:6, 4:6] = 1
    b = a.clone()

    result = fourier_ring_correlation(a, b)
    assert result.shape == (2, 6)
    assert torch.allclose(result, torch.ones(2, 6))

    # Multiple batch dimensions
    a = torch.zeros((3, 2, 10, 10))
    a[:, :, 4:6, 4:6] = 1
    b = a.clone()

    result = fourier_ring_correlation(a, b)
    assert result.shape == (3, 2, 6)
    assert torch.allclose(result, torch.ones(3, 2, 6))


def test_fourier_shell_correlation_batched():
    """Test 3D fourier shell correlation with batching."""
    # Single batch
    a = torch.zeros((2, 10, 10, 10))
    a[:, 4:6, 4:6, 4:6] = 1
    b = a.clone()

    result = fourier_shell_correlation(a, b)
    assert result.shape == (2, 6)
    assert torch.allclose(result, torch.ones(2, 6))

    # Multiple batch dimensions
    a = torch.zeros((3, 2, 10, 10, 10))
    a[:, :, 4:6, 4:6, 4:6] = 1
    b = a.clone()

    result = fourier_shell_correlation(a, b)
    assert result.shape == (3, 2, 6)
    assert torch.allclose(result, torch.ones(3, 2, 6))


def test_batched_vs_individual_processing():
    """Test that batched processing gets the same results as individual processing."""
    torch.manual_seed(42)  # For reproducible results

    # Test 2D case
    batch_size = 3
    a_2d_batch = torch.rand((batch_size, 16, 16))
    b_2d_batch = torch.rand((batch_size, 16, 16))

    # Process as batch
    result_batch = fourier_ring_correlation(a_2d_batch, b_2d_batch)

    # Process individually
    individual_results = []
    for i in range(batch_size):
        result_individual = fourier_ring_correlation(a_2d_batch[i], b_2d_batch[i])
        individual_results.append(result_individual)
    result_individual_stacked = torch.stack(individual_results)

    # Should be identical
    assert torch.allclose(result_batch, result_individual_stacked, atol=1e-6)

    # Test 3D case
    a_3d_batch = torch.rand((batch_size, 12, 12, 12))
    b_3d_batch = torch.rand((batch_size, 12, 12, 12))

    # Process as batch
    result_batch_3d = fourier_shell_correlation(a_3d_batch, b_3d_batch)

    # Process individually
    individual_results_3d = []
    for i in range(batch_size):
        result_individual_3d = fourier_shell_correlation(a_3d_batch[i], b_3d_batch[i])
        individual_results_3d.append(result_individual_3d)
    result_individual_stacked_3d = torch.stack(individual_results_3d)

    # Should be identical
    assert torch.allclose(result_batch_3d, result_individual_stacked_3d, atol=1e-6)


def test_multidimensional_batched_vs_individual():
    """Test multi-dimensional batching gets same results as individual processing."""
    torch.manual_seed(42)

    # Test 2D case with multiple batch dimensions
    batch_shape = (2, 3)
    a_2d_multi = torch.rand((*batch_shape, 16, 16))
    b_2d_multi = torch.rand((*batch_shape, 16, 16))

    # Process as multi-batch
    result_multi_batch = fourier_ring_correlation(a_2d_multi, b_2d_multi)

    # Process individually and reconstruct
    individual_results = []
    for i in range(batch_shape[0]):
        for j in range(batch_shape[1]):
            result_individual = fourier_ring_correlation(
                a_2d_multi[i, j], b_2d_multi[i, j]
            )
            individual_results.append(result_individual)

    # Reshape to match multi-batch result
    result_individual_reshaped = torch.stack(individual_results).view(*batch_shape, -1)

    # Should be identical
    assert torch.allclose(result_multi_batch, result_individual_reshaped, atol=1e-6)


def test_edge_cases():
    """Test edge cases like identical images, zeros, and ones."""
    # Test batched edge cases
    a_batch = torch.stack([torch.ones((12, 12, 12)), torch.zeros((12, 12, 12))])
    b_batch = a_batch.clone()

    result_batch = fourier_shell_correlation(a_batch, b_batch)

    # Process individually for comparison
    result_individual_0 = fourier_shell_correlation(a_batch[0], b_batch[0])
    result_individual_1 = fourier_shell_correlation(a_batch[1], b_batch[1])

    assert torch.allclose(result_batch[0], result_individual_0)
    assert torch.allclose(result_batch[1], result_individual_1)


def test_rectangular_images():
    """Test that rectangular images work correctly."""
    torch.manual_seed(42)

    # Test 2D rectangular images
    a_rect = torch.rand((8, 12))  # 8x12 rectangular image
    b_rect = torch.rand((8, 12))

    # Should work without error
    result_rect = fourier_ring_correlation(a_rect, b_rect)

    # Should have min(8, 12) // 2 + 1 = 5 bins
    assert result_rect.shape == (5,)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result_rect >= -1)
    assert torch.all(result_rect <= 1)

    # Test 3D rectangular volumes
    a_rect_3d = torch.rand((8, 10, 12))  # 8x10x12 rectangular volume
    b_rect_3d = torch.rand((8, 10, 12))

    # Should work without error
    result_rect_3d = fourier_shell_correlation(a_rect_3d, b_rect_3d)

    # Should have min(8, 10, 12) // 2 + 1 = 5 bins
    assert result_rect_3d.shape == (5,)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result_rect_3d >= -1)
    assert torch.all(result_rect_3d <= 1)


def test_rectangular_images_batched():
    """Test that rectangular images work correctly with batching."""
    torch.manual_seed(42)

    # Test 2D rectangular images with batching
    batch_size = 3
    a_rect_batch = torch.rand((batch_size, 8, 12))  # 8x12 rectangular images
    b_rect_batch = torch.rand((batch_size, 8, 12))

    # Should work without error
    result_rect_batch = fourier_ring_correlation(a_rect_batch, b_rect_batch)

    # Should have shape (batch_size, min(8, 12) // 2 + 1) = (3, 5)
    assert result_rect_batch.shape == (3, 5)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result_rect_batch >= -1)
    assert torch.all(result_rect_batch <= 1)

    # Test 3D rectangular volumes with batching
    a_rect_3d_batch = torch.rand((batch_size, 6, 8, 10))  # 6x8x10 rectangular volumes
    b_rect_3d_batch = torch.rand((batch_size, 6, 8, 10))

    # Should work without error
    result_rect_3d_batch = fourier_shell_correlation(a_rect_3d_batch, b_rect_3d_batch)

    # Should have shape (batch_size, min(6, 8, 10) // 2 + 1) = (3, 4)
    assert result_rect_3d_batch.shape == (3, 4)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result_rect_3d_batch >= -1)
    assert torch.all(result_rect_3d_batch <= 1)


def test_identical_rectangular_images():
    """Test that identical rectangular images produce correlation of 1."""
    torch.manual_seed(42)

    # Test 2D identical rectangular images
    a_rect = torch.rand((8, 12))  # 8x12 rectangular image
    b_rect = a_rect.clone()

    result_rect = fourier_ring_correlation(a_rect, b_rect)

    # Identical images should have correlation close to 1
    assert torch.allclose(result_rect, torch.ones_like(result_rect), atol=1e-6)

    # Test 3D identical rectangular volumes
    a_rect_3d = torch.rand((6, 8, 10))  # 6x8x10 rectangular volume
    b_rect_3d = a_rect_3d.clone()

    result_rect_3d = fourier_shell_correlation(a_rect_3d, b_rect_3d)

    # Identical images should have correlation close to 1
    assert torch.allclose(result_rect_3d, torch.ones_like(result_rect_3d), atol=1e-6)


def test_broadcasting_one_to_many():
    """Test broadcasting: one tensor to many (e.g., a: (N, h, w), b: (h, w))."""
    torch.manual_seed(42)

    # Test 2D broadcasting
    a_many = torch.rand((5, 8, 12))  # Many images
    b_single = torch.rand((8, 12))  # Single image

    result = fourier_ring_correlation(a_many, b_single)

    # Should have shape (5, min(8, 12) // 2 + 1) = (5, 5)
    assert result.shape == (5, 5)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result >= -1)
    assert torch.all(result <= 1)

    # Test 3D broadcasting
    a_many_3d = torch.rand((3, 6, 8, 10))  # Many volumes
    b_single_3d = torch.rand((6, 8, 10))  # Single volume

    result_3d = fourier_shell_correlation(a_many_3d, b_single_3d)

    # Should have shape (3, min(6, 8, 10) // 2 + 1) = (3, 4)
    assert result_3d.shape == (3, 4)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result_3d >= -1)
    assert torch.all(result_3d <= 1)


def test_broadcasting_many_to_many():
    """Test broadcasting: many to many (e.g., a: (10, 1, h, w), b: (1, 10, h, w))."""
    torch.manual_seed(42)

    # Test 2D broadcasting
    a_many = torch.rand((10, 1, 8, 12))  # Shape for broadcasting
    b_many = torch.rand((1, 10, 8, 12))  # Shape for broadcasting

    result = fourier_ring_correlation(a_many, b_many)

    # Should have shape (10, 10, min(8, 12) // 2 + 1) = (10, 10, 5)
    assert result.shape == (10, 10, 5)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result >= -1)
    assert torch.all(result <= 1)

    # Test 3D broadcasting
    a_many_3d = torch.rand((4, 1, 6, 8, 10))  # Shape for broadcasting
    b_many_3d = torch.rand((1, 4, 6, 8, 10))  # Shape for broadcasting

    result_3d = fourier_shell_correlation(a_many_3d, b_many_3d)

    # Should have shape (4, 4, min(6, 8, 10) // 2 + 1) = (4, 4, 4)
    assert result_3d.shape == (4, 4, 4)

    # Correlation should be bounded between -1 and 1
    assert torch.all(result_3d >= -1)
    assert torch.all(result_3d <= 1)


def test_broadcasting_vs_individual():
    """Test that broadcasting gives same results as individual computations."""
    torch.manual_seed(42)

    # Create test data
    a_single = torch.rand((8, 12))  # Single image
    b_batch = torch.rand((3, 8, 12))  # Batch of images

    # Compute using broadcasting
    result_broadcast = fourier_ring_correlation(b_batch, a_single)

    # Compute individually
    results_individual = []
    for i in range(3):
        result_individual = fourier_ring_correlation(b_batch[i], a_single)
        results_individual.append(result_individual)
    result_individual_stacked = torch.stack(results_individual)

    # Should be identical (within numerical precision)
    assert torch.allclose(result_broadcast, result_individual_stacked, atol=1e-6)


def test_broadcasting_invalid_spatial_dims():
    """Test that broadcasting fails when spatial dimensions don't match."""
    torch.manual_seed(42)

    # Test 2D with mismatched spatial dimensions
    a = torch.rand((2, 8, 12))
    b = torch.rand((2, 10, 14))  # Different spatial dimensions

    with pytest.raises(ValueError, match="Spatial dimensions must match"):
        fourier_ring_correlation(a, b)

    # Test 3D with mismatched spatial dimensions
    a_3d = torch.rand((2, 6, 8, 10))
    b_3d = torch.rand((2, 8, 10, 12))  # Different spatial dimensions

    with pytest.raises(ValueError, match="Spatial dimensions must match"):
        fourier_shell_correlation(a_3d, b_3d)


# --- Modified Fourier Shell Correlation (mFSC) Tests ---


def test_mfsc_exports():
    """Test that mFSC functions are importable from package root and in __all__."""
    import torch_fourier_shell_correlation

    # Check functions are importable (already done via top-level import)
    assert callable(modified_fourier_ring_correlation)
    assert callable(modified_fourier_shell_correlation)

    # Check they are in __all__
    assert "modified_fourier_ring_correlation" in torch_fourier_shell_correlation.__all__
    assert "modified_fourier_shell_correlation" in torch_fourier_shell_correlation.__all__


def test_modified_fourier_ring_correlation():
    """Test 2D mFRC: identical images with all-ones mask should give correlations near 1."""
    torch.manual_seed(42)
    a = torch.rand((16, 16))
    b = a.clone()
    mask = torch.ones((16, 16))

    result = modified_fourier_ring_correlation(a, b, mask)

    # Output should have correct number of shells
    n_shells = min(16, 16) // 2 + 1  # 9
    assert result.shape == (n_shells,)

    # Identical images should have correlation near 1 for all shells
    assert torch.allclose(result, torch.ones(n_shells), atol=0.05)


def test_modified_fourier_shell_correlation():
    """Test 3D mFSC: identical volumes with all-ones mask should give correlations near 1."""
    torch.manual_seed(42)
    a = torch.rand((16, 16, 16))
    b = a.clone()
    mask = torch.ones((16, 16, 16))

    result = modified_fourier_shell_correlation(a, b, mask)

    # Output should have correct number of shells
    n_shells = min(16, 16, 16) // 2 + 1  # 9
    assert result.shape == (n_shells,)

    # Identical volumes should have correlation near 1 for all shells
    assert torch.allclose(result, torch.ones(n_shells), atol=0.05)


def test_mfsc_output_shape():
    """Test that mFSC output shape is min(spatial_dims) // 2 + 1."""
    torch.manual_seed(42)

    # 2D square
    a_sq = torch.rand((16, 16))
    mask_sq = torch.ones((16, 16))
    result_sq = modified_fourier_ring_correlation(a_sq, a_sq.clone(), mask_sq)
    assert result_sq.shape == (9,)  # 16 // 2 + 1 = 9

    # 2D rectangular
    a_rect = torch.rand((12, 16))
    mask_rect = torch.ones((12, 16))
    result_rect = modified_fourier_ring_correlation(a_rect, a_rect.clone(), mask_rect)
    assert result_rect.shape == (7,)  # min(12, 16) // 2 + 1 = 7

    # 3D cubic
    a_3d = torch.rand((16, 16, 16))
    mask_3d = torch.ones((16, 16, 16))
    result_3d = modified_fourier_shell_correlation(a_3d, a_3d.clone(), mask_3d)
    assert result_3d.shape == (9,)  # 16 // 2 + 1 = 9

    # 3D rectangular
    a_3d_rect = torch.rand((10, 14, 16))
    mask_3d_rect = torch.ones((10, 14, 16))
    result_3d_rect = modified_fourier_shell_correlation(
        a_3d_rect, a_3d_rect.clone(), mask_3d_rect
    )
    assert result_3d_rect.shape == (6,)  # min(10, 14, 16) // 2 + 1 = 6


def test_mfsc_sigma_parameter():
    """Test that different sigma values produce different correlation curves."""
    torch.manual_seed(42)
    a = torch.rand((16, 16))
    b = torch.rand((16, 16))
    mask = torch.ones((16, 16))

    result_default = modified_fourier_ring_correlation(a, b, mask, sigma_pixels=1.0)
    result_narrow = modified_fourier_ring_correlation(a, b, mask, sigma_pixels=0.5)
    result_wide = modified_fourier_ring_correlation(a, b, mask, sigma_pixels=2.0)

    # Different sigma values should produce different results
    assert not torch.allclose(result_default, result_narrow, atol=1e-4)
    assert not torch.allclose(result_default, result_wide, atol=1e-4)


def test_mfsc_batched():
    """Test batched mFSC: output batch dims match input batch dims."""
    torch.manual_seed(42)

    # 2D batched
    batch_size = 3
    a_2d_batch = torch.rand((batch_size, 16, 16))
    b_2d_batch = torch.rand((batch_size, 16, 16))
    mask_2d = torch.ones((16, 16))

    result_2d = modified_fourier_ring_correlation(a_2d_batch, b_2d_batch, mask_2d)
    assert result_2d.shape == (batch_size, 9)  # (3, min(16,16)//2+1)

    # Verify batched matches individual processing
    for i in range(batch_size):
        result_individual = modified_fourier_ring_correlation(
            a_2d_batch[i], b_2d_batch[i], mask_2d
        )
        assert torch.allclose(result_2d[i], result_individual, atol=1e-6)

    # 3D batched
    a_3d_batch = torch.rand((2, 12, 12, 12))
    b_3d_batch = torch.rand((2, 12, 12, 12))
    mask_3d = torch.ones((12, 12, 12))

    result_3d = modified_fourier_shell_correlation(a_3d_batch, b_3d_batch, mask_3d)
    assert result_3d.shape == (2, 7)  # (2, min(12,12,12)//2+1)

    # Verify batched matches individual processing
    for i in range(2):
        result_individual_3d = modified_fourier_shell_correlation(
            a_3d_batch[i], b_3d_batch[i], mask_3d
        )
        assert torch.allclose(result_3d[i], result_individual_3d, atol=1e-6)


def test_mfsc_uncorrelated_noise():
    """Test that mFSC of uncorrelated noise returns near-zero correlations."""
    torch.manual_seed(42)
    a = torch.randn((16, 16))
    torch.manual_seed(137)
    b = torch.randn((16, 16))
    mask = torch.ones((16, 16))

    result = modified_fourier_ring_correlation(a, b, mask)

    # Shell 0 (DC) is always 1.0
    assert result[0] == 1.0

    # Non-DC shells should be near zero for uncorrelated noise
    # Allow generous tolerance since 16x16 is small
    assert torch.all(torch.abs(result[1:]) < 0.5)
