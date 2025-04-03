// jest.config.ts

import type { JestConfigWithTsJest } from 'ts-jest';

const config: JestConfigWithTsJest = {
  testEnvironment: 'jsdom', // for React projects
  transform: {
    // Use @swc/jest to handle TypeScript and JSX transformation
    "^.+\\.[jt]sx?$": "@swc/jest",
  },
  transformIgnorePatterns: [
    "node_modules/(?!(your-module-name)/)", // Adjust this for custom modules
  ],
  moduleNameMapper: {
    // For handling CSS modules
    "\\.(css|scss|less)$": "identity-obj-proxy",
  },
  setupFilesAfterEnv: [
    "@testing-library/jest-dom", // for additional matchers
  ],
};

export default config;
