const js = require('@eslint/js');
const tsParser = require('@typescript-eslint/parser');
const tsPlugin = require('@typescript-eslint/eslint-plugin');
const globals = require('globals');

module.exports = [
    js.configs.recommended,
    {
        files: ['src/**/*.ts'],
        languageOptions: {
            parser: tsParser,
            parserOptions: {
                ecmaVersion: 6,
                sourceType: 'module'
            },
            globals: {
                ...globals.node,
                console: 'readonly',
                require: 'readonly',
                setTimeout: 'readonly'
            }
        },
        plugins: {
            '@typescript-eslint': tsPlugin
        },
        rules: {
            'curly': 'warn',
            'eqeqeq': 'warn',
            'no-throw-literal': 'warn',
            'semi': 'warn',
            'no-unused-vars': 'off'  // 关闭未使用变量检查，因为有些是为了完整性保留的
        }
    },
    {
        files: ['src/test/**/*.ts'],
        languageOptions: {
            globals: {
                ...globals.node,
                ...globals.mocha,
                suite: 'readonly',
                test: 'readonly'
            }
        }
    },
    {
        ignores: ['out/', 'dist/', '**/*.d.ts', 'node_modules/']
    }
];