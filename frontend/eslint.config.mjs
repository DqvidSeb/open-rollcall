import { dirname } from 'path';
import { fileURLToPath } from 'url';
import { FlatCompat } from '@eslint/eslintrc';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

const compat = new FlatCompat({
  baseDirectory: __dirname,
});

const eslintConfig = [
  ...compat.extends('next/core-web-vitals', 'next/typescript'),
  {
    rules: {
      // No unused vars — remove them instead of commenting out
      '@typescript-eslint/no-unused-vars': ['error', { argsIgnorePattern: '^_' }],
      // Prefer const
      'prefer-const': 'error',
      // No explicit any without justification comment
      '@typescript-eslint/no-explicit-any': 'warn',
      // No console.log in production code
      'no-console': ['warn', { allow: ['error', 'warn'] }],
    },
  },
];

export default eslintConfig;
