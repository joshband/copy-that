import { useState, useEffect } from 'react';
import { CubeIcon, MagnifyingGlassIcon } from '@heroicons/react/24/outline';

interface ComponentLibraryBrowserProps {
  projectId: string;
  components: Record<string, any>;
  onComponentSelect?: (componentType: string, variantKey: string) => void;
}

export default function ComponentLibraryBrowser({
  projectId,
  components,
  onComponentSelect,
}: ComponentLibraryBrowserProps) {
  const [selectedComponent, setSelectedComponent] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterSize, setFilterSize] = useState<string>('all');
  const [filterState, setFilterState] = useState<string>('all');

  // Select first component by default
  useEffect(() => {
    if (!selectedComponent && Object.keys(components).length > 0) {
      setSelectedComponent(Object.keys(components)[0]);
    }
  }, [components, selectedComponent]);

  if (!components || Object.keys(components).length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-8 text-center">
        <CubeIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
        <p className="text-gray-600">No components generated yet</p>
      </div>
    );
  }

  const componentTypes = Object.keys(components);
  const currentComponent = selectedComponent ? components[selectedComponent] : null;

  // Filter variants
  const filteredVariants = currentComponent
    ? Object.entries(currentComponent.variants || {}).filter(([key, _]) => {
        if (searchQuery && !key.toLowerCase().includes(searchQuery.toLowerCase())) {
          return false;
        }
        if (filterSize !== 'all' && !key.includes(filterSize)) {
          return false;
        }
        if (filterState !== 'all' && !key.includes(filterState)) {
          return false;
        }
        return true;
      })
    : [];

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-green-600 to-green-700 px-6 py-4">
        <div className="flex items-center gap-2 text-white">
          <CubeIcon className="h-6 w-6" />
          <h2 className="text-xl font-semibold">Component Library</h2>
        </div>
        <p className="text-green-100 text-sm mt-1">
          {componentTypes.length} component families, {Object.values(components).reduce(
            (sum, comp) => sum + Object.keys(comp.variants || {}).length,
            0
          )}{' '}
          total variants
        </p>
      </div>

      <div className="flex h-[600px]">
        {/* Sidebar - Component Types */}
        <div className="w-64 border-r border-gray-200 overflow-y-auto bg-gray-50">
          <div className="p-4">
            <h3 className="text-xs font-semibold text-gray-700 uppercase mb-2">
              Components
            </h3>
            <div className="space-y-1">
              {componentTypes.map((type) => (
                <button
                  key={type}
                  onClick={() => setSelectedComponent(type)}
                  className={`w-full text-left px-3 py-2 rounded-lg text-sm transition-colors ${
                    selectedComponent === type
                      ? 'bg-green-600 text-white'
                      : 'text-gray-700 hover:bg-gray-200'
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span className="capitalize">{type}</span>
                    <span className="text-xs opacity-75">
                      {Object.keys(components[type].variants || {}).length}
                    </span>
                  </div>
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 overflow-y-auto">
          <div className="p-6">
            {currentComponent && (
              <>
                {/* Filters */}
                <div className="mb-6 space-y-3">
                  {/* Search */}
                  <div className="relative">
                    <MagnifyingGlassIcon className="absolute left-3 top-1/2 -translate-y-1/2 h-5 w-5 text-gray-400" />
                    <input
                      type="text"
                      placeholder="Search variants..."
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    />
                  </div>

                  {/* Filters */}
                  <div className="flex gap-3">
                    <select
                      value={filterSize}
                      onChange={(e) => setFilterSize(e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      <option value="all">All Sizes</option>
                      <option value="sm">Small</option>
                      <option value="md">Medium</option>
                      <option value="lg">Large</option>
                      <option value="xl">X-Large</option>
                    </select>

                    <select
                      value={filterState}
                      onChange={(e) => setFilterState(e.target.value)}
                      className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
                    >
                      <option value="all">All States</option>
                      <option value="default">Default</option>
                      <option value="hover">Hover</option>
                      <option value="active">Active</option>
                      <option value="disabled">Disabled</option>
                      <option value="focus">Focus</option>
                    </select>
                  </div>
                </div>

                {/* Component Info */}
                <div className="mb-6 p-4 bg-gray-50 rounded-lg">
                  <h3 className="font-semibold text-gray-900 capitalize mb-1">
                    {selectedComponent}
                  </h3>
                  <p className="text-sm text-gray-600">
                    {currentComponent.description}
                  </p>
                  <div className="mt-2 text-xs text-gray-500">
                    Type: <span className="font-medium">{currentComponent.type}</span> •{' '}
                    Variants: <span className="font-medium">{filteredVariants.length}</span>
                  </div>
                </div>

                {/* Variants Grid */}
                <div className="grid grid-cols-2 lg:grid-cols-3 gap-4">
                  {filteredVariants.map(([variantKey, variantData]: [string, any]) => (
                    <button
                      key={variantKey}
                      onClick={() => onComponentSelect?.(selectedComponent, variantKey)}
                      className="group relative p-4 border-2 border-gray-200 rounded-lg hover:border-green-500 hover:shadow-lg transition-all bg-white"
                    >
                      {/* SVG Preview */}
                      <div
                        className="w-full aspect-square flex items-center justify-center bg-gray-50 rounded-md mb-3 overflow-hidden"
                        dangerouslySetInnerHTML={{ __html: variantData.svg }}
                      />

                      {/* Variant Info */}
                      <div className="text-left">
                        <p className="text-sm font-medium text-gray-900 truncate">
                          {variantKey}
                        </p>
                        {variantData.dimensions && (
                          <p className="text-xs text-gray-500">
                            {variantData.dimensions.width}×{variantData.dimensions.height}
                          </p>
                        )}
                      </div>

                      {/* Hover overlay */}
                      <div className="absolute inset-0 bg-green-600 bg-opacity-0 group-hover:bg-opacity-5 rounded-lg transition-all pointer-events-none" />
                    </button>
                  ))}
                </div>

                {filteredVariants.length === 0 && (
                  <div className="text-center py-12">
                    <p className="text-gray-500">No variants match your filters</p>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
