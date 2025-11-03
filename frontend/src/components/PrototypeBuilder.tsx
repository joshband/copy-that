import { useState } from 'react';
import { PaintBrushIcon, TrashIcon, ArrowDownTrayIcon } from '@heroicons/react/24/outline';

interface PrototypeElement {
  id: string;
  componentType: string;
  variantKey: string;
  svg: string;
  x: number;
  y: number;
  width: number;
  height: number;
}

interface PrototypeBuilderProps {
  projectName: string;
  onExport?: () => void;
}

export default function PrototypeBuilder({ projectName, onExport }: PrototypeBuilderProps) {
  const [elements, setElements] = useState<PrototypeElement[]>([]);
  const [selectedElement, setSelectedElement] = useState<string | null>(null);
  const [canvasSize, setCanvasSize] = useState({ width: 1200, height: 800 });

  const addElement = (componentType: string, variantKey: string, svg: string) => {
    const newElement: PrototypeElement = {
      id: Math.random().toString(36).substr(2, 9),
      componentType,
      variantKey,
      svg,
      x: 50,
      y: 50,
      width: 150,
      height: 50,
    };

    setElements([...elements, newElement]);
    setSelectedElement(newElement.id);
  };

  const removeElement = (id: string) => {
    setElements(elements.filter((el) => el.id !== id));
    if (selectedElement === id) {
      setSelectedElement(null);
    }
  };

  const clearCanvas = () => {
    if (confirm('Clear all elements from the canvas?')) {
      setElements([]);
      setSelectedElement(null);
    }
  };

  const exportPrototype = () => {
    // Create SVG of entire canvas
    const svgContent = `
      <svg width="${canvasSize.width}" height="${canvasSize.height}" xmlns="http://www.w3.org/2000/svg">
        <rect width="100%" height="100%" fill="#f9fafb"/>
        ${elements.map((el) => `
          <g transform="translate(${el.x}, ${el.y})">
            ${el.svg}
          </g>
        `).join('')}
      </svg>
    `;

    // Download
    const blob = new Blob([svgContent], { type: 'image/svg+xml' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${projectName}-prototype.svg`;
    a.click();
    URL.revokeObjectURL(url);

    onExport?.();
  };

  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-white">
            <PaintBrushIcon className="h-6 w-6" />
            <h2 className="text-xl font-semibold">Prototype Builder</h2>
          </div>

          <div className="flex gap-2">
            <button
              onClick={clearCanvas}
              className="px-4 py-2 bg-white bg-opacity-20 hover:bg-opacity-30 text-white rounded-lg transition-colors text-sm font-medium flex items-center gap-2"
            >
              <TrashIcon className="h-4 w-4" />
              Clear
            </button>
            <button
              onClick={exportPrototype}
              disabled={elements.length === 0}
              className="px-4 py-2 bg-white text-purple-700 hover:bg-opacity-90 rounded-lg transition-colors text-sm font-medium flex items-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <ArrowDownTrayIcon className="h-4 w-4" />
              Export
            </button>
          </div>
        </div>
        <p className="text-purple-100 text-sm mt-1">
          {elements.length} {elements.length === 1 ? 'element' : 'elements'} on canvas
        </p>
      </div>

      {/* Canvas */}
      <div className="p-6">
        <div
          className="relative border-2 border-dashed border-gray-300 rounded-lg bg-gray-50 overflow-auto"
          style={{ width: '100%', height: `${canvasSize.height}px` }}
        >
          {elements.length === 0 ? (
            <div className="absolute inset-0 flex items-center justify-center">
              <div className="text-center">
                <PaintBrushIcon className="h-12 w-12 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-600 font-medium">
                  Click on components in the library to add them
                </p>
                <p className="text-sm text-gray-500 mt-1">
                  Build your prototype by arranging UI elements
                </p>
              </div>
            </div>
          ) : (
            <div className="relative" style={{ width: canvasSize.width, height: canvasSize.height }}>
              {elements.map((element) => (
                <div
                  key={element.id}
                  className={`absolute cursor-move group ${
                    selectedElement === element.id ? 'ring-2 ring-purple-500' : ''
                  }`}
                  style={{
                    left: element.x,
                    top: element.y,
                  }}
                  onClick={() => setSelectedElement(element.id)}
                >
                  <div
                    className="bg-white rounded shadow-sm"
                    dangerouslySetInnerHTML={{ __html: element.svg }}
                  />

                  {/* Remove button */}
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      removeElement(element.id);
                    }}
                    className="absolute -top-2 -right-2 p-1 bg-red-500 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity shadow-lg"
                  >
                    <TrashIcon className="h-3 w-3" />
                  </button>

                  {/* Label */}
                  <div className="absolute -top-6 left-0 text-xs bg-black text-white px-2 py-1 rounded opacity-0 group-hover:opacity-100 transition-opacity whitespace-nowrap">
                    {element.componentType} - {element.variantKey}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Instructions */}
        <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h4 className="text-sm font-semibold text-blue-900 mb-2">How to use:</h4>
          <ul className="text-sm text-blue-800 space-y-1">
            <li>• Click on components in the library to add them to the canvas</li>
            <li>• Drag elements to reposition them (coming soon)</li>
            <li>• Click "Export" to download your prototype as SVG</li>
          </ul>
        </div>
      </div>
    </div>
  );
}
