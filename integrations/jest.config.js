/** @type {import("jest").Config} **/
module.exports = {
  testEnvironment: 'node',
  transform: {
    '^.+\\.tsx?$': [
      'ts-jest',
      {
        diagnostics: false,
      },
    ],
  },
  moduleNameMapper: {
    '^@cyberintel/shared$': '<rootDir>/../shared/src/index.ts',
    '^@cyberintel/shared/(.*)$': '<rootDir>/../shared/src/$1'
  }
};
