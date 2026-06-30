module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  moduleNameMapper: {
    '^@cyberintel/shared(.*)$': '<rootDir>/../shared/src$1',
    '^@cyberintel/integrations(.*)$': '<rootDir>/../integrations/src$1'
  },
  testMatch: ['**/*.test.ts'],
  transform: {
    '^.+\\.tsx?$': ['ts-jest', {
      diagnostics: false,
    }],
  },
};
