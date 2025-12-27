import pytest
from unittest.mock import patch, MagicMock
from tools import search_influencers


class TestSearchInfluencers:
    """Test cases for the search_influencers function."""

    @patch('tools.client')
    def test_search_influencers_success(self, mock_client):
        """Test successful influencer search with valid API response."""
        # Arrange
        mock_run = {'defaultDatasetId': 'test_dataset'}
        mock_client.actor.return_value.call.return_value = mock_run
        mock_items = [
            {'username': 'user1', 'followersCount': 1000, 'biography': 'Bio 1'},
            {'username': 'user2', 'followersCount': 2000, 'biography': 'Bio 2'}
        ]
        mock_client.dataset.return_value.iterate_items.return_value = mock_items

        # Act
        result = search_influencers('fitness')

        # Assert
        assert len(result) == 2
        assert result[0]['username'] == 'user1'
        assert result[0]['followers'] == 1000
        assert result[0]['bio'] == 'Bio 1'
        assert result[1]['username'] == 'user2'
        assert result[1]['followers'] == 2000
        assert result[1]['bio'] == 'Bio 2'
        mock_client.actor.assert_called_once_with("apify/instagram-scraper")
        mock_client.actor.return_value.call.assert_called_once_with(run_input={
            "search": "fitness",
            "searchType": "user",
            "resultsLimit": 3
        })

    @patch('tools.client')
    def test_search_influencers_api_failure(self, mock_client):
        """Test fallback to mock data when API call fails."""
        # Arrange
        mock_client.actor.side_effect = Exception("API Error")

        # Act
        result = search_influencers('fitness')

        # Assert
        assert len(result) == 1
        assert result[0]['username'] == 'test_user'
        assert result[0]['followers'] == 5000
        assert result[0]['bio'] == 'Mock bio'

    @patch('tools.client')
    def test_search_influencers_empty_results(self, mock_client):
        """Test handling of empty results from API."""
        # Arrange
        mock_run = {'defaultDatasetId': 'test_dataset'}
        mock_client.actor.return_value.call.return_value = mock_run
        mock_client.dataset.return_value.iterate_items.return_value = []

        # Act
        result = search_influencers('nonexistent_niche')

        # Assert
        assert result == []

    @patch('tools.client')
    def test_search_influencers_missing_fields(self, mock_client):
        """Test handling of items missing expected fields."""
        # Arrange
        mock_run = {'defaultDatasetId': 'test_dataset'}
        mock_client.actor.return_value.call.return_value = mock_run
        mock_items = [
            {'username': 'user1'},  # Missing followers and bio
            {'followersCount': 1000, 'biography': 'Bio'},  # Missing username
        ]
        mock_client.dataset.return_value.iterate_items.return_value = mock_items

        # Act
        result = search_influencers('fitness')

        # Assert
        assert len(result) == 2
        assert result[0]['username'] == 'user1'
        assert result[0]['followers'] is None
        assert result[0]['bio'] is None
        assert result[1]['username'] is None
        assert result[1]['followers'] == 1000
        assert result[1]['bio'] == 'Bio'

    def test_search_influencers_invalid_niche(self):
        """Test with invalid niche input (empty string)."""
        with patch('tools.client') as mock_client:
            mock_run = {'defaultDatasetId': 'test_dataset'}
            mock_client.actor.return_value.call.return_value = mock_run
            mock_client.dataset.return_value.iterate_items.return_value = []

            result = search_influencers('')

            assert result == []
            mock_client.actor.return_value.call.assert_called_once_with(run_input={
                "search": "",
                "searchType": "user",
                "resultsLimit": 3
            })

    @patch('tools.client')
    @patch('tools.time.sleep')
    def test_search_influencers_retry_success_on_third_attempt(self, mock_sleep, mock_client):
        """Test successful retry after two failures."""
        # Arrange
        mock_client.actor.return_value.call.side_effect = [
            Exception("Timeout 1"),
            Exception("Timeout 2"),
            {'defaultDatasetId': 'test_dataset'},
        ]
        mock_items = [{'username': 'user1', 'followersCount': 1000, 'biography': 'Bio 1'}]
        mock_client.dataset.return_value.iterate_items.return_value = mock_items

        # Act
        result = search_influencers('fitness')

        # Assert
        assert len(result) == 1
        assert result[0]['username'] == 'user1'
        assert mock_client.actor.return_value.call.call_count == 3
        assert mock_sleep.call_count == 2  # Sleep called twice before success
        mock_sleep.assert_any_call(5)

    @patch('tools.client')
    @patch('tools.time.sleep')
    def test_search_influencers_retry_exhaustion_fallback_to_mock(self, mock_sleep, mock_client):
        """Test fallback to mock data after all retries fail."""
        # Arrange
        mock_client.actor.return_value.call.side_effect = Exception("Persistent API Error")

        # Act
        result = search_influencers('fitness')

        # Assert
        assert len(result) == 1
        assert result[0]['username'] == 'test_user'
        assert result[0]['followers'] == 5000
        assert result[0]['bio'] == 'Mock bio'
        assert mock_client.actor.return_value.call.call_count == 3  # All retries attempted
        assert mock_sleep.call_count == 2  # Sleep called between retries

    @patch('tools.client')
    @patch('tools.time.sleep')
    def test_search_influencers_custom_retry_parameters(self, mock_sleep, mock_client):
        """Test custom retry parameters work correctly."""
        # Arrange
        mock_client.actor.return_value.call.side_effect = [Exception("Error 1"), {'defaultDatasetId': 'test_dataset'}]
        mock_items = [{'username': 'user1', 'followersCount': 1000, 'biography': 'Bio 1'}]
        mock_client.dataset.return_value.iterate_items.return_value = mock_items

        # Act
        result = search_influencers('fitness', max_retries=2, retry_delay=10)

        # Assert
        assert len(result) == 1
        assert result[0]['username'] == 'user1'
        assert mock_client.actor.return_value.call.call_count == 2
        mock_sleep.assert_called_once_with(10)