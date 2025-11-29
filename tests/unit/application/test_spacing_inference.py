from copy_that.application.spacing_utils import cluster_spacing_values, spacing_tokens_from_values


def test_cluster_spacing_values_merges_nearby():
    values = [4, 8, 8, 9, 16]
    clustered = cluster_spacing_values(values, tolerance=0.15)
    assert clustered == [4, 8, 16]


def test_spacing_tokens_from_values_outputs_dimensions():
    values = [7, 8, 15, 16]
    tokens = spacing_tokens_from_values(values)
    assert list(tokens.keys()) == ["spacing.1", "spacing.2", "spacing.3"]
    assert tokens["spacing.2"]["$value"]["unit"] == "px"
    assert tokens["spacing.2"]["$type"] == "dimension"
