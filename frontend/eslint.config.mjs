import nextCoreWebVitals from 'eslint-config-next/core-web-vitals';
import nextTypescript from 'eslint-config-next/typescript';

const eslintConfig = [
  ...nextCoreWebVitals,
  ...nextTypescript,
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
      // eslint-plugin-react-hooks v7's React Compiler rule flags the standard
      // "fetch on mount" / "sync external API on mount" effects used throughout
      // this codebase (data fetching hooks, theme/media-query sync, etc.).
      // These patterns are correct under React 19 without the compiler, so the
      // rule is disabled rather than rewritten into Suspense/useSyncExternalStore.
      'react-hooks/set-state-in-effect': 'off',
    },
  },
];

export default eslintConfig;
