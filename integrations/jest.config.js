module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  testMatch: ['**/*.test.ts'],
  moduleNameMapper: {
    '^@cyberintel/(.*)$': '<rootDir>/../$1/src',
  }
};
