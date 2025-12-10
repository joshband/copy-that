"""Metric provider registry for auto-discovery and management.

The registry:
- Discovers available providers
- Loads them in order
- Provides access by name or tier
- Enables easy addition of new providers
"""

import inspect

from .base import MetricProvider, MetricTier


class MetricProviderRegistry:
    """Registry for discovering and managing metric providers."""

    def __init__(self):
        self._providers: dict[str, MetricProvider] = {}
        self._by_tier: dict[MetricTier, list[MetricProvider]] = {tier: [] for tier in MetricTier}

    def register(self, provider: MetricProvider) -> None:
        """Register a metric provider instance.

        Args:
            provider: An instance of MetricProvider subclass
        """
        if not isinstance(provider, MetricProvider):
            raise TypeError(f"{provider} must be a MetricProvider subclass")

        name = provider.name
        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered")

        self._providers[name] = provider
        self._by_tier[provider.tier].append(provider)

    def discover_and_register(self, module) -> None:
        """Auto-discover and register all MetricProvider subclasses in a module.

        Args:
            module: Python module to search for providers
        """
        for _name, obj in inspect.getmembers(module):
            if (
                inspect.isclass(obj)
                and issubclass(obj, MetricProvider)
                and obj is not MetricProvider
            ):
                provider = obj()
                try:
                    self.register(provider)
                except ValueError:
                    pass  # Already registered

    def get_provider(self, name: str) -> MetricProvider | None:
        """Get a provider by name.

        Args:
            name: Provider name

        Returns:
            Provider instance or None if not found
        """
        return self._providers.get(name)

    def get_providers_by_tier(self, tier: MetricTier) -> list[MetricProvider]:
        """Get all providers for a specific tier.

        Args:
            tier: Metric tier

        Returns:
            List of providers for that tier, sorted by priority
        """
        providers = self._by_tier[tier]
        return sorted(providers, key=lambda p: p.priority)

    def get_all_providers(self) -> list[MetricProvider]:
        """Get all registered providers, sorted by priority.

        Returns:
            All providers sorted by priority (tier, then name)
        """
        all_providers = list(self._providers.values())
        return sorted(all_providers, key=lambda p: (p.priority, p.name))

    def get_provider_names(self) -> list[str]:
        """Get all registered provider names.

        Returns:
            List of provider names
        """
        return sorted(self._providers.keys())

    def __len__(self) -> int:
        """Number of registered providers."""
        return len(self._providers)

    def __repr__(self) -> str:
        """String representation showing registered providers."""
        providers_str = ", ".join(self.get_provider_names())
        return f"MetricProviderRegistry([{providers_str}])"
