import prettier from 'eslint-config-prettier';
import path from 'node:path';
import js from '@eslint/js';
import svelte from 'eslint-plugin-svelte';
import { defineConfig, includeIgnoreFile } from 'eslint/config';
import globals from 'globals';
import ts from 'typescript-eslint';

const gitignorePath = path.resolve(import.meta.dirname, '.gitignore');

export default defineConfig(
	includeIgnoreFile(gitignorePath),
	js.configs.recommended,
	ts.configs.recommended,
	svelte.configs.recommended,
	prettier,
	svelte.configs.prettier,
	{
		languageOptions: { globals: { ...globals.browser, ...globals.node } },
		rules: {
			// typescript-eslint strongly recommend that you do not use the no-undef lint rule on TypeScript projects.
			// see: https://typescript-eslint.io/troubleshooting/faqs/eslint/#i-get-errors-from-the-no-undef-rule-about-global-variables-not-being-defined-even-though-there-are-no-typescript-errors
			'no-undef': 'off'
		}
	},
	{
		files: ['**/*.svelte', '**/*.svelte.ts', '**/*.svelte.js'],
		languageOptions: {
			parserOptions: {
				projectService: true,
				extraFileExtensions: ['.svelte'],
				parser: ts.parser
			}
		}
	},
	{
		// Mechanizable code rules (docs/vibe-coding-rules.md).
		rules: {
			complexity: ['error', 8],
			'max-depth': ['error', 3],
			'no-console': 'error',
			'no-param-reassign': 'error',
			'no-magic-numbers': 'off',
			'@typescript-eslint/no-magic-numbers': [
				'error',
				{ ignore: [-1, 0, 1, 2], ignoreEnums: true, ignoreReadonlyClassProperties: true }
			]
		}
	},
	{
		files: ['**/*.spec.ts', '**/*.e2e.ts', '*.config.ts', '*.config.js'],
		rules: { '@typescript-eslint/no-magic-numbers': 'off' }
	}
);
