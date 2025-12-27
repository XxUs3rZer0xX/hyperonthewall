import pytest
from unittest.mock import patch, MagicMock
from main import graph, AgentState


class TestLangGraphWorkflow:
    """Integration tests for the LangGraph workflow."""

    @patch('agents.search_influencers')  # Patch the real API call
    @patch('agents.llm')  # Patch the LLM at the source
    def test_workflow_success(self, mock_llm, mock_search):
        """Test successful execution of the full workflow."""
        # Arrange
        mock_search.return_value = [
            {'username': 'user1', 'followers': 1000, 'bio': 'Test bio'}
        ]
        mock_llm.invoke.return_value = MagicMock(content='Test emails')

        inputs = {"user_request": "fitness"}

        # Act
        results = list(graph.stream(inputs))

        # Assert
        assert len(results) == 2
        assert 'scout' in results[0]
        assert 'manager' in results[1]
        assert 'user1 (1000 followers): Test bio' in results[0]['scout']['influencer_list']
        assert results[1]['manager']['outreach_emails'] == 'Test emails'

    @patch('agents.search_influencers')
    def test_workflow_scout_failure(self, mock_search):
        """Test workflow when scout_agent fails."""
        # Arrange
        mock_search.side_effect = Exception("Scout error")

        inputs = {"user_request": "fitness"}

        # Act & Assert
        with pytest.raises(Exception, match="Scout error"):
            list(graph.stream(inputs))

    @patch('agents.search_influencers')
    @patch('agents.llm')
    def test_workflow_manager_failure(self, mock_llm, mock_search):
        """Test workflow when manager_agent fails."""
        # Arrange
        mock_search.return_value = [
            {'username': 'user1', 'followers': 1000, 'bio': 'Test bio'}
        ]
        mock_llm.invoke.side_effect = Exception("Manager error")

        inputs = {"user_request": "fitness"}

        # Act & Assert - LangGraph handles exceptions internally
        with pytest.raises(Exception, match="Manager error"):
            list(graph.stream(inputs))

    @patch('agents.search_influencers')
    @patch('agents.llm')
    def test_workflow_empty_input(self, mock_llm, mock_search):
        """Test workflow with empty user request."""
        mock_search.return_value = []
        mock_llm.invoke.return_value = MagicMock(content='Mock emails')

        inputs = {"user_request": ""}

        results = list(graph.stream(inputs))

        assert len(results) == 2
        assert results[0]['scout']['influencer_list'] == ""
        assert results[1]['manager']['outreach_emails'] == 'Mock emails'

    def test_workflow_missing_user_request(self):
        """Test workflow with missing user_request key."""
        inputs = {}  # Missing user_request

        with pytest.raises(KeyError):
            list(graph.stream(inputs))

    def test_agent_state_typed_dict(self):
        """Test that AgentState TypedDict works correctly."""
        state: AgentState = {
            "user_request": "test",
            "influencer_list": "list",
            "outreach_emails": "emails"
        }
        assert state["user_request"] == "test"
        assert state["influencer_list"] == "list"
        assert state["outreach_emails"] == "emails"

    def test_graph_compilation(self):
        """Test that the graph compiles correctly."""
        assert graph is not None
        assert hasattr(graph, 'stream')
        assert hasattr(graph, 'invoke')