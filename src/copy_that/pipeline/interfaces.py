"""
Pipeline interfaces module

Contains abstract base classes for pipeline agents:
- BasePipelineAgent: ABC for all pipeline agents
"""

from abc import ABC, abstractmethod

from copy_that.pipeline.types import PipelineTask, TokenResult


class BasePipelineAgent(ABC):
    """
    Abstract base class for all pipeline agents.

    Each pipeline agent is responsible for a specific stage in the
    token extraction pipeline. Agents must implement:
    - process(): Main processing logic for tasks
    - health_check(): Health/readiness check
    - agent_type: Property identifying the agent type
    - stage_name: Property identifying the pipeline stage

    Example implementation:
        class ColorExtractionAgent(BasePipelineAgent):
            @property
            def agent_type(self) -> str:
                return "color_extractor"

            @property
            def stage_name(self) -> str:
                return "extraction"

            async def process(self, task: PipelineTask) -> list[TokenResult]:
                # Extract colors from image
                return [TokenResult(...)]

            async def health_check(self) -> bool:
                return True
    """

    @property
    @abstractmethod
    def agent_type(self) -> str:
        """
        Return the agent type identifier.

        This uniquely identifies the type of agent (e.g., 'color_extractor',
        'typography_extractor', 'aggregator').

        Returns:
            String identifier for this agent type
        """
        pass

    @property
    @abstractmethod
    def stage_name(self) -> str:
        """
        Return the pipeline stage name.

        Identifies which stage of the pipeline this agent operates in
        (e.g., 'preprocessing', 'extraction', 'aggregation', 'validation',
        'generation').

        Returns:
            String name of the pipeline stage
        """
        pass

    @abstractmethod
    async def process(self, task: PipelineTask) -> list[TokenResult]:
        """
        Process a pipeline task and return token results.

        This is the main entry point for the agent's processing logic.
        It receives a task definition and returns extracted/processed tokens.

        Args:
            task: The pipeline task containing image URL and configuration

        Returns:
            List of TokenResult objects from this processing stage

        Raises:
            PipelineError: If processing fails
        """
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """
        Check if the agent is healthy and ready to process tasks.

        This method should verify that all required resources are available
        (API keys, model access, database connections, etc.).

        Returns:
            True if the agent is healthy and ready, False otherwise
        """
        pass
