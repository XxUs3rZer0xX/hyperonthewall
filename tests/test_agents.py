import pytest
from unittest.mock import patch, MagicMock
from agents import scout_agent, manager_agent


class TestScoutAgent:
    """Test cases for the scout_agent function."""

    @patch('agents.search_influencers')
    def test_scout_agent_success(self, mock_search):
        """Test scout_agent with successful influencer search."""
        # Arrange
        mock_search.return_value = [
            {'username': 'user1', 'followers': 1000, 'bio': 'Fitness enthusiast'},
            {'username': 'user2', 'followers': 2000, 'bio': 'Yoga teacher'}
        ]
        state = {'user_request': 'fitness'}

        # Act
        result = scout_agent(state)

        # Assert
        expected_list = "- user1 (1000 followers): Fitness enthusiast\n- user2 (2000 followers): Yoga teacher"
        assert result['influencer_list'] == expected_list
        mock_search.assert_called_once_with('fitness')

    @patch('agents.search_influencers')
    def test_scout_agent_empty_results(self, mock_search):
        """Test scout_agent with no influencers found."""
        # Arrange
        mock_search.return_value = []
        state = {'user_request': 'nonexistent_niche'}

        # Act
        result = scout_agent(state)

        # Assert
        assert result['influencer_list'] == ""
        mock_search.assert_called_once_with('nonexistent_niche')

    @patch('agents.search_influencers')
    def test_scout_agent_missing_fields(self, mock_search):
        """Test scout_agent with incomplete influencer data."""
        # Arrange
        mock_search.return_value = [
            {'username': 'user1', 'followers': None, 'bio': 'Bio'},
            {'username': None, 'followers': 1000, 'bio': None}
        ]
        state = {'user_request': 'test'}

        # Act
        result = scout_agent(state)

        # Assert
        expected_list = "- user1 (None followers): Bio\n- None (1000 followers): None"
        assert result['influencer_list'] == expected_list

    def test_scout_agent_missing_request(self):
        """Test scout_agent with missing user_request in state."""
        with patch('agents.search_influencers') as mock_search:
            mock_search.return_value = []
            state = {}  # Missing user_request

            with pytest.raises(KeyError):
                scout_agent(state)


class TestManagerAgent:
    """Test cases for the manager_agent function."""

    @patch('agents.llm')
    def test_manager_agent_with_llm(self, mock_llm):
        """Test manager_agent when LLM is available."""
        # Arrange
        mock_response = MagicMock()
        mock_response.content = "Generated outreach brief"
        mock_llm.invoke.return_value = mock_response
        state = {
            'influencer_list': 'Influencer data',
            'user_request': 'fitness'
        }

        # Act
        result = manager_agent(state)

        # Assert
        assert result['outreach_emails'] == "Generated outreach brief"
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        assert len(call_args) == 2
        assert call_args[0].content == 'You are a Manager.'
        assert 'Create a brief for: Influencer data' in call_args[1]

    def test_manager_agent_without_llm(self):
        """Test manager_agent when LLM is not available (None)."""
        # Arrange
        with patch('agents.llm', None):
            state = {
                'influencer_list': 'Influencer data',
                'user_request': 'fitness'
            }

            # Act
            result = manager_agent(state)

            # Assert
            assert result['outreach_emails'] == "Mock: outreach emails generated"

    @patch('agents.llm')
    def test_manager_agent_llm_error(self, mock_llm):
        """Test manager_agent when LLM invocation fails."""
        # Arrange
        mock_llm.invoke.side_effect = Exception("LLM Error")
        state = {
            'influencer_list': 'Influencer data',
            'user_request': 'fitness'
        }

        # Act & Assert
        with pytest.raises(Exception, match="LLM Error"):
            manager_agent(state)

    def test_manager_agent_missing_state_keys(self):
        """Test manager_agent with missing state keys."""
        with patch('agents.llm', None):
            state = {}  # Missing influencer_list

            # Should not raise error, but return mock
            result = manager_agent(state)
            assert result['outreach_emails'] == "Mock: outreach emails generated"