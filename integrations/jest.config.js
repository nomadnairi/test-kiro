module.exports = {
  preset: 'ts-jest',
  testEnvironment: 'node',
  moduleNameMapper: {
    '^@cyberintel/shared(.*)$': '<rootDir>/../shared/src$1'
  },
  transform: {
    '^.+\\.tsx?$': ['ts-jest', { diagnostics: false }]
  }
};
