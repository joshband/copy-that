# Copy That - Frontend

React + TypeScript frontend for the Copy That design system generator.

## Features

- **Drag & Drop Upload**: Upload up to 10 reference images
- **Image Preview**: Visual preview grid with hover actions
- **Validation**: File type and size validation
- **Responsive Design**: Works on desktop, tablet, and mobile
- **Error Handling**: Clear error messages for invalid files

## Tech Stack

- **React 18** with TypeScript
- **Vite** for fast development
- **Tailwind CSS** for styling
- **React Dropzone** for drag-and-drop
- **Heroicons** for icons

## Getting Started

### Install Dependencies

\`\`\`bash
npm install
\`\`\`

### Run Development Server

\`\`\`bash
npm run dev
\`\`\`

The app will be available at \`http://localhost:5173/\`

### Build for Production

\`\`\`bash
npm run build
\`\`\`

## Project Structure

\`\`\`
frontend/
├── src/
│   ├── components/
│   │   └── ImageUploader.tsx   # Main upload component
│   ├── App.tsx                  # Root component
│   ├── index.css                # Tailwind imports
│   └── main.tsx                 # App entry point
├── public/                       # Static assets
├── index.html                    # HTML template
├── package.json                  # Dependencies
├── tailwind.config.js            # Tailwind configuration
├── postcss.config.js             # PostCSS configuration
├── tsconfig.json                 # TypeScript configuration
└── vite.config.ts                # Vite configuration
\`\`\`

## Component: ImageUploader

### Features

- Accepts up to 10 images
- File size limit: 10MB per image
- Supported formats: JPG, PNG, WebP, GIF
- Drag & drop or click to select
- Individual image removal
- Clear all functionality
- Image preview grid with hover effects
- Filename display on hover

### Usage

\`\`\`tsx
import ImageUploader from './components/ImageUploader';

function App() {
  return <ImageUploader />;
}
\`\`\`

## Development

### Adding New Components

1. Create component in \`src/components/\`
2. Import in \`App.tsx\` or parent component
3. Add types in component file or \`src/types/\`

### Styling

Using Tailwind CSS utility classes.

## Scripts

- \`npm run dev\` - Start development server
- \`npm run build\` - Build for production
- \`npm run preview\` - Preview production build
- \`npm run lint\` - Run ESLint

## License

[License type to be determined]
