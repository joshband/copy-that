"""Tests for ProvenanceTracker class

Tests for tracking which images contributed to each token,
calculating weighted confidence scores, and storing provenance data.
"""

from dataclasses import fields
from datetime import datetime, timedelta

import pytest

from copy_that.pipeline import TokenResult, TokenType
from copy_that.pipeline.aggregation.provenance import ProvenanceRecord, ProvenanceTracker


class TestProvenanceRecord:
    """Test ProvenanceRecord dataclass structure"""

    def test_provenance_record_dataclass(self):
        """Test ProvenanceRecord is a dataclass with correct fields"""
        # Verify it's a dataclass by checking for __dataclass_fields__
        assert hasattr(ProvenanceRecord, "__dataclass_fields__")

        # Get field names
        field_names = {f.name for f in fields(ProvenanceRecord)}

        # Verify required fields
        assert "image_id" in field_names
        assert "confidence" in field_names
        assert "timestamp" in field_names
        assert "metadata" in field_names

    def test_provenance_record_creation(self):
        """Test creating a ProvenanceRecord"""
        timestamp = datetime.utcnow()
        record = ProvenanceRecord(
            image_id="img-001",
            confidence=0.95,
            timestamp=timestamp,
            metadata={"extractor": "color_agent"},
        )

        assert record.image_id == "img-001"
        assert record.confidence == 0.95
        assert record.timestamp == timestamp
        assert record.metadata == {"extractor": "color_agent"}

    def test_provenance_record_with_empty_metadata(self):
        """Test ProvenanceRecord with empty metadata"""
        record = ProvenanceRecord(
            image_id="img-002",
            confidence=0.8,
            timestamp=datetime.utcnow(),
            metadata={},
        )

        assert record.metadata == {}

    def test_provenance_record_with_none_metadata(self):
        """Test ProvenanceRecord with None metadata"""
        record = ProvenanceRecord(
            image_id="img-003",
            confidence=0.75,
            timestamp=datetime.utcnow(),
            metadata=None,
        )

        assert record.metadata is None


class TestProvenanceTrackerBasic:
    """Test basic ProvenanceTracker functionality"""

    def test_empty_tracker(self):
        """Test empty tracker has no provenance"""
        tracker = ProvenanceTracker()

        # Should have no tracked tokens
        assert tracker.get_tracked_token_ids() == []

        # Getting sources for non-existent token returns empty
        sources = tracker.get_source_images("nonexistent-token")
        assert sources == []

    def test_add_single_source(self):
        """Test adding provenance for one image"""
        tracker = ProvenanceTracker()
        timestamp = datetime.utcnow()

        record = ProvenanceRecord(
            image_id="img-001",
            confidence=0.92,
            timestamp=timestamp,
            metadata={"source": "upload"},
        )

        tracker.add_provenance("token-123", record)

        # Verify token is tracked
        assert "token-123" in tracker.get_tracked_token_ids()

        # Verify source is retrievable
        sources = tracker.get_source_images("token-123")
        assert len(sources) == 1
        assert sources[0] == "img-001"

    def test_add_multiple_sources(self):
        """Test tracking multiple images for same token"""
        tracker = ProvenanceTracker()

        # Add multiple sources for the same token
        records = [
            ProvenanceRecord(
                image_id="img-001",
                confidence=0.85,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
            ProvenanceRecord(
                image_id="img-002",
                confidence=0.90,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
            ProvenanceRecord(
                image_id="img-003",
                confidence=0.78,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        ]

        for record in records:
            tracker.add_provenance("token-456", record)

        # All sources should be tracked
        sources = tracker.get_source_images("token-456")
        assert len(sources) == 3
        assert set(sources) == {"img-001", "img-002", "img-003"}

    def test_get_source_images(self):
        """Test retrieving all sources for a token"""
        tracker = ProvenanceTracker()

        # Add provenance from multiple images
        tracker.add_provenance(
            "primary-color",
            ProvenanceRecord(
                image_id="hero-banner",
                confidence=0.95,
                timestamp=datetime.utcnow(),
                metadata={"region": "header"},
            ),
        )
        tracker.add_provenance(
            "primary-color",
            ProvenanceRecord(
                image_id="logo-image",
                confidence=0.88,
                timestamp=datetime.utcnow(),
                metadata={"region": "logo"},
            ),
        )

        sources = tracker.get_source_images("primary-color")
        assert "hero-banner" in sources
        assert "logo-image" in sources


class TestConfidenceCalculation:
    """Test confidence calculation and aggregation"""

    def test_calculate_weighted_confidence(self):
        """Test weighted confidence calculation based on source count and confidence"""
        tracker = ProvenanceTracker()

        # Add multiple sources with different confidences
        tracker.add_provenance(
            "token-a",
            ProvenanceRecord(
                image_id="img-1",
                confidence=0.9,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )
        tracker.add_provenance(
            "token-a",
            ProvenanceRecord(
                image_id="img-2",
                confidence=0.8,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )
        tracker.add_provenance(
            "token-a",
            ProvenanceRecord(
                image_id="img-3",
                confidence=0.7,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        weighted_confidence = tracker.calculate_weighted_confidence("token-a")

        # Should be a valid confidence value
        assert 0.0 <= weighted_confidence <= 1.0

        # Should take into account multiple sources and their confidences
        # With 3 sources at 0.9, 0.8, 0.7 - result should be reasonably high
        assert weighted_confidence > 0.5

    def test_confidence_capped_at_one(self):
        """Test that weighted confidence never exceeds 1.0"""
        tracker = ProvenanceTracker()

        # Add many high-confidence sources
        for i in range(10):
            tracker.add_provenance(
                "high-conf-token",
                ProvenanceRecord(
                    image_id=f"img-{i}",
                    confidence=0.99,
                    timestamp=datetime.utcnow(),
                    metadata=None,
                ),
            )

        weighted_confidence = tracker.calculate_weighted_confidence("high-conf-token")

        # Must be capped at 1.0
        assert weighted_confidence <= 1.0
        # Should be very high given all the high-confidence sources
        assert weighted_confidence > 0.9

    def test_confidence_aggregation_formula(self):
        """Test the specific confidence aggregation formula"""
        tracker = ProvenanceTracker()

        # Add two sources with known confidences
        tracker.add_provenance(
            "formula-test",
            ProvenanceRecord(
                image_id="img-a",
                confidence=0.8,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )
        tracker.add_provenance(
            "formula-test",
            ProvenanceRecord(
                image_id="img-b",
                confidence=0.6,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        weighted_confidence = tracker.calculate_weighted_confidence("formula-test")

        # The formula should combine confidences - commonly:
        # 1 - product of (1 - confidence_i) = 1 - (1-0.8)(1-0.6) = 1 - 0.2*0.4 = 0.92
        # Or weighted average: (0.8 + 0.6) / 2 = 0.7
        # The exact formula depends on implementation
        # Key property: result should be higher than individual lowest confidence
        # when there are multiple confirming sources
        assert weighted_confidence >= 0.6  # At least as high as lowest
        assert weighted_confidence <= 1.0

    def test_single_source_confidence(self):
        """Test confidence calculation with single source"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "single-source",
            ProvenanceRecord(
                image_id="only-img",
                confidence=0.75,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        weighted_confidence = tracker.calculate_weighted_confidence("single-source")

        # With single source, weighted confidence should equal the source confidence
        assert weighted_confidence == pytest.approx(0.75, abs=0.01)

    def test_confidence_for_nonexistent_token(self):
        """Test confidence calculation for non-existent token"""
        tracker = ProvenanceTracker()

        weighted_confidence = tracker.calculate_weighted_confidence("does-not-exist")

        # Should return 0.0 for non-existent token
        assert weighted_confidence == 0.0


class TestProvenanceMerging:
    """Test merging provenance records when deduplicating tokens"""

    def test_merge_provenance_records(self):
        """Test merging provenance when deduplicating tokens"""
        tracker = ProvenanceTracker()

        # Add provenance for first instance of token
        tracker.add_provenance(
            "token-original",
            ProvenanceRecord(
                image_id="img-1",
                confidence=0.85,
                timestamp=datetime.utcnow(),
                metadata={"extractor": "agent-a"},
            ),
        )
        tracker.add_provenance(
            "token-original",
            ProvenanceRecord(
                image_id="img-2",
                confidence=0.80,
                timestamp=datetime.utcnow(),
                metadata={"extractor": "agent-a"},
            ),
        )

        # Add provenance for duplicate token
        tracker.add_provenance(
            "token-duplicate",
            ProvenanceRecord(
                image_id="img-3",
                confidence=0.90,
                timestamp=datetime.utcnow(),
                metadata={"extractor": "agent-b"},
            ),
        )

        # Merge duplicate into original
        tracker.merge_provenance("token-original", "token-duplicate")

        # Original should have all sources
        sources = tracker.get_source_images("token-original")
        assert len(sources) == 3
        assert set(sources) == {"img-1", "img-2", "img-3"}

        # Duplicate still exists (merge copies records, doesn't delete)
        assert "token-duplicate" in tracker.get_tracked_token_ids()

    def test_merge_preserves_metadata(self):
        """Test that merge preserves metadata from both tokens"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "token-a",
            ProvenanceRecord(
                image_id="img-1",
                confidence=0.85,
                timestamp=datetime.utcnow(),
                metadata={"key": "value-1"},
            ),
        )
        tracker.add_provenance(
            "token-b",
            ProvenanceRecord(
                image_id="img-2",
                confidence=0.90,
                timestamp=datetime.utcnow(),
                metadata={"key": "value-2"},
            ),
        )

        tracker.merge_provenance("token-a", "token-b")

        # Get all records for merged token
        records = tracker.get_provenance_records("token-a")
        assert len(records) == 2

        # Both metadata should be preserved
        metadata_values = [r.metadata.get("key") for r in records if r.metadata]
        assert "value-1" in metadata_values
        assert "value-2" in metadata_values

    def test_merge_nonexistent_source(self):
        """Test merging from non-existent token does nothing"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "existing-token",
            ProvenanceRecord(
                image_id="img-1",
                confidence=0.85,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        # Should not raise error
        tracker.merge_provenance("existing-token", "nonexistent-token")

        # Original unchanged
        sources = tracker.get_source_images("existing-token")
        assert len(sources) == 1


class TestTimestampTracking:
    """Test timestamp tracking functionality"""

    def test_track_extraction_timestamp(self):
        """Test that extraction timestamp is recorded"""
        tracker = ProvenanceTracker()

        before_time = datetime.utcnow()
        timestamp = datetime.utcnow()
        after_time = datetime.utcnow()

        record = ProvenanceRecord(
            image_id="img-001",
            confidence=0.9,
            timestamp=timestamp,
            metadata=None,
        )

        tracker.add_provenance("timestamped-token", record)

        records = tracker.get_provenance_records("timestamped-token")
        assert len(records) == 1

        recorded_timestamp = records[0].timestamp
        assert before_time <= recorded_timestamp <= after_time

    def test_multiple_timestamps_preserved(self):
        """Test that multiple timestamps are preserved"""
        tracker = ProvenanceTracker()

        # Add records at different times
        time1 = datetime.utcnow()
        tracker.add_provenance(
            "multi-time",
            ProvenanceRecord(
                image_id="img-1",
                confidence=0.85,
                timestamp=time1,
                metadata=None,
            ),
        )

        time2 = time1 + timedelta(seconds=1)
        tracker.add_provenance(
            "multi-time",
            ProvenanceRecord(
                image_id="img-2",
                confidence=0.90,
                timestamp=time2,
                metadata=None,
            ),
        )

        records = tracker.get_provenance_records("multi-time")
        timestamps = [r.timestamp for r in records]

        assert len(timestamps) == 2
        # Both timestamps should be present
        assert any(abs((t - time1).total_seconds()) < 0.001 for t in timestamps)
        assert any(abs((t - time2).total_seconds()) < 0.001 for t in timestamps)


class TestSourceUniqueness:
    """Test source image ID uniqueness"""

    def test_source_image_ids_unique(self):
        """Test that duplicate source IDs are not added multiple times"""
        tracker = ProvenanceTracker()

        # Add same image ID multiple times
        for _ in range(3):
            tracker.add_provenance(
                "dup-source-token",
                ProvenanceRecord(
                    image_id="same-image",
                    confidence=0.85,
                    timestamp=datetime.utcnow(),
                    metadata=None,
                ),
            )

        sources = tracker.get_source_images("dup-source-token")

        # Should only have unique image IDs
        assert len(sources) == len(set(sources))
        # Depending on implementation, might keep first or all records
        # but get_source_images should return unique IDs
        assert "same-image" in sources

    def test_different_images_all_tracked(self):
        """Test that different image IDs are all tracked"""
        tracker = ProvenanceTracker()

        image_ids = ["img-a", "img-b", "img-c", "img-d"]
        for img_id in image_ids:
            tracker.add_provenance(
                "multi-img-token",
                ProvenanceRecord(
                    image_id=img_id,
                    confidence=0.8,
                    timestamp=datetime.utcnow(),
                    metadata=None,
                ),
            )

        sources = tracker.get_source_images("multi-img-token")
        assert set(sources) == set(image_ids)


class TestTokenExtensionsIntegration:
    """Test provenance storage in W3C token extensions"""

    def test_provenance_in_token_extensions(self):
        """Test that provenance is stored in W3C extensions field"""
        tracker = ProvenanceTracker()

        # Add provenance data
        tracker.add_provenance(
            "ext-token",
            ProvenanceRecord(
                image_id="img-001",
                confidence=0.92,
                timestamp=datetime.utcnow(),
                metadata={"extractor": "color_agent"},
            ),
        )
        tracker.add_provenance(
            "ext-token",
            ProvenanceRecord(
                image_id="img-002",
                confidence=0.88,
                timestamp=datetime.utcnow(),
                metadata={"extractor": "color_agent"},
            ),
        )

        # Create a token and apply provenance to its extensions
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="primary",
            value="#FF6B35",
            confidence=0.9,
        )

        # Apply provenance to token
        updated_token = tracker.apply_to_token("ext-token", token)

        # Check extensions field
        assert updated_token.extensions is not None
        assert "com.copythat.provenance" in updated_token.extensions

        provenance_ext = updated_token.extensions["com.copythat.provenance"]
        assert "sources" in provenance_ext
        assert "img-001" in provenance_ext["sources"]
        assert "img-002" in provenance_ext["sources"]

    def test_provenance_extensions_include_confidence(self):
        """Test that provenance extensions include weighted confidence"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "conf-ext-token",
            ProvenanceRecord(
                image_id="img-001",
                confidence=0.85,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        token = TokenResult(
            token_type=TokenType.COLOR,
            name="secondary",
            value="#3498DB",
            confidence=0.85,
        )

        updated_token = tracker.apply_to_token("conf-ext-token", token)

        provenance_ext = updated_token.extensions["com.copythat.provenance"]
        assert "weighted_confidence" in provenance_ext
        assert 0.0 <= provenance_ext["weighted_confidence"] <= 1.0

    def test_apply_to_token_preserves_existing_extensions(self):
        """Test that applying provenance preserves existing extensions"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "preserve-ext",
            ProvenanceRecord(
                image_id="img-001",
                confidence=0.9,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        # Token with existing extensions
        token = TokenResult(
            token_type=TokenType.COLOR,
            name="accent",
            value="#E74C3C",
            confidence=0.9,
            extensions={"com.figma": {"variableId": "var-123"}},
        )

        updated_token = tracker.apply_to_token("preserve-ext", token)

        # Both extensions should be present
        assert "com.figma" in updated_token.extensions
        assert "com.copythat.provenance" in updated_token.extensions
        assert updated_token.extensions["com.figma"]["variableId"] == "var-123"

    def test_apply_to_nonexistent_token(self):
        """Test applying provenance for non-existent token returns original"""
        tracker = ProvenanceTracker()

        token = TokenResult(
            token_type=TokenType.COLOR,
            name="test",
            value="#000000",
            confidence=0.5,
        )

        # Should return token unchanged (or with empty provenance)
        result = tracker.apply_to_token("nonexistent", token)
        assert result.name == "test"
        assert result.value == "#000000"


class TestEdgeCases:
    """Test edge cases and boundary conditions"""

    def test_zero_confidence_record(self):
        """Test handling of zero confidence record"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "zero-conf",
            ProvenanceRecord(
                image_id="uncertain-img",
                confidence=0.0,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        sources = tracker.get_source_images("zero-conf")
        assert len(sources) == 1

        confidence = tracker.calculate_weighted_confidence("zero-conf")
        assert confidence == 0.0

    def test_max_confidence_record(self):
        """Test handling of maximum confidence record"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "max-conf",
            ProvenanceRecord(
                image_id="certain-img",
                confidence=1.0,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        confidence = tracker.calculate_weighted_confidence("max-conf")
        assert confidence == 1.0

    def test_many_sources_same_token(self):
        """Test handling many sources for same token"""
        tracker = ProvenanceTracker()

        # Add 100 sources
        for i in range(100):
            tracker.add_provenance(
                "many-sources",
                ProvenanceRecord(
                    image_id=f"img-{i:03d}",
                    confidence=0.5 + (i * 0.005),  # Range from 0.5 to 0.995
                    timestamp=datetime.utcnow(),
                    metadata=None,
                ),
            )

        sources = tracker.get_source_images("many-sources")
        assert len(sources) == 100

        confidence = tracker.calculate_weighted_confidence("many-sources")
        assert 0.0 <= confidence <= 1.0

    def test_token_id_with_special_characters(self):
        """Test token IDs with special characters"""
        tracker = ProvenanceTracker()

        special_ids = [
            "color.primary.brand",
            "spacing-xs-mobile",
            "font_family_heading",
            "shadow/card/elevated",
        ]

        for token_id in special_ids:
            tracker.add_provenance(
                token_id,
                ProvenanceRecord(
                    image_id="img-001",
                    confidence=0.9,
                    timestamp=datetime.utcnow(),
                    metadata=None,
                ),
            )

        for token_id in special_ids:
            sources = tracker.get_source_images(token_id)
            assert len(sources) == 1

    def test_get_provenance_records_ordering(self):
        """Test that provenance records maintain order"""
        tracker = ProvenanceTracker()

        # Add records with specific timestamps
        base_time = datetime.utcnow()
        for i in range(5):
            tracker.add_provenance(
                "ordered-token",
                ProvenanceRecord(
                    image_id=f"img-{i}",
                    confidence=0.8,
                    timestamp=base_time + timedelta(seconds=i),
                    metadata={"order": i},
                ),
            )

        records = tracker.get_provenance_records("ordered-token")
        assert len(records) == 5

        # Verify all records are present
        orders = [r.metadata["order"] for r in records]
        assert set(orders) == {0, 1, 2, 3, 4}


class TestTrackerState:
    """Test tracker state management"""

    def test_multiple_tokens_tracked(self):
        """Test tracking multiple different tokens"""
        tracker = ProvenanceTracker()

        token_ids = ["color-primary", "spacing-base", "font-heading"]

        for token_id in token_ids:
            tracker.add_provenance(
                token_id,
                ProvenanceRecord(
                    image_id="img-001",
                    confidence=0.9,
                    timestamp=datetime.utcnow(),
                    metadata=None,
                ),
            )

        tracked = tracker.get_tracked_token_ids()
        assert set(tracked) == set(token_ids)

    def test_clear_provenance(self):
        """Test clearing provenance for a token"""
        tracker = ProvenanceTracker()

        tracker.add_provenance(
            "to-clear",
            ProvenanceRecord(
                image_id="img-001",
                confidence=0.9,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        assert "to-clear" in tracker.get_tracked_token_ids()

        # Clear the provenance
        tracker.clear_provenance("to-clear")

        assert "to-clear" not in tracker.get_tracked_token_ids()
        assert tracker.get_source_images("to-clear") == []

    def test_get_all_source_images(self):
        """Test getting all unique source images across all tokens"""
        tracker = ProvenanceTracker()

        # Add same image to multiple tokens
        tracker.add_provenance(
            "token-1",
            ProvenanceRecord(
                image_id="shared-img",
                confidence=0.9,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )
        tracker.add_provenance(
            "token-2",
            ProvenanceRecord(
                image_id="shared-img",
                confidence=0.85,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )
        tracker.add_provenance(
            "token-2",
            ProvenanceRecord(
                image_id="unique-img",
                confidence=0.8,
                timestamp=datetime.utcnow(),
                metadata=None,
            ),
        )

        all_sources = tracker.get_all_source_images()
        assert set(all_sources) == {"shared-img", "unique-img"}
