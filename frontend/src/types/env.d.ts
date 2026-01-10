/// <reference types="react-scripts" />

declare namespace NodeJS {
  interface ProcessEnv {
    REACT_APP_API_BASE_URL?: string;
  }
}

declare var process: {
  env: NodeJS.ProcessEnv;
};

