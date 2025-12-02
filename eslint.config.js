import js from '@eslint/js';
import globals from 'globals';
import react from 'eslint-plugin-react';
import reactHooks from 'eslint-plugin-react-hooks';
import typescript from '@typescript-eslint/eslint-plugin';
import typescriptParser from '@typescript-eslint/parser';

export default [
  {
    ignores: [
      '**/dist/**',
      '**/build/**',
      '**/node_modules/**',
      '**/.venv/**',
      '**/coverage/**',
      '**/htmlcov/**',
      '**/static/**',
      '**/*.config.ts',
      '**/*.config.js',
      '.eslintrc*',
      '*.min.js',
    ],
  },

  {
    files: ['src/**/*.{ts,tsx}', 'frontend/src/**/*.{ts,tsx}'],
    languageOptions: {
      parser: typescriptParser,
      parserOptions: {
        ecmaVersion: 2020,
        sourceType: 'module',
        ecmaFeatures: {
          jsx: true,
        },
        project: ['./tsconfig.json', './frontend/tsconfig.json'],
        tsconfigRootDir: process.cwd(),
      },
      globals: {
        ...globals.browser,
        ...globals.es2020,
      },
    },
    plugins: {
      '@typescript-eslint': typescript,
      react,
      'react-hooks': reactHooks,
    },
    rules: {
      ...js.configs.recommended.rules,
      ...typescript.configs['recommended'].rules,
      ...typescript.configs['recommended-requiring-type-checking'].rules,
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,

      // TypeScript rules
      '@typescript-eslint/no-explicit-any': 'off',
      '@typescript-eslint/no-unsafe-assignment': 'off',
      '@typescript-eslint/no-unsafe-member-access': 'off',
      '@typescript-eslint/no-unsafe-return': 'off',
      '@typescript-eslint/no-unsafe-call': 'off',
      '@typescript-eslint/no-unsafe-argument': 'off',
      '@typescript-eslint/no-unused-vars': 'off',
      '@typescript-eslint/require-await': 'off',
      '@typescript-eslint/no-floating-promises': 'warn',
      '@typescript-eslint/no-redundant-type-constituents': 'warn',
      '@typescript-eslint/prefer-promise-reject-errors': 'warn',
      '@typescript-eslint/restrict-template-expressions': 'warn',
      '@typescript-eslint/no-base-to-string': 'warn',

      // React rules
      'react/react-in-jsx-scope': 'off', // React 17+ JSX transform
      'react/prop-types': 'off', // Using TypeScript for prop validation
      'react/display-name': 'warn',
      'react/no-unescaped-entities': 'warn',
      'react-hooks/rules-of-hooks': 'error',
      'react-hooks/exhaustive-deps': 'warn',

      // General rules
      'no-console': ['warn', { allow: ['warn', 'error'] }],
      'prefer-const': 'warn',
      'eqeqeq': 'warn',
      'no-undef': 'warn',
      '@typescript-eslint/only-throw-error': 'warn',
    },
    settings: {
      react: {
        version: 'detect',
      },
    },
  },

  {
    files: ['**/*.{js,mjs,cjs}'],
    languageOptions: {
      sourceType: 'module',
      ecmaVersion: 2020,
      globals: globals.node,
    },
    rules: {
      ...js.configs.recommended.rules,
    },
  },
];
