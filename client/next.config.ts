import type { NextConfig } from 'next';
import path from 'path';

const nextConfig: NextConfig = {
  // Enables standalone output for Docker (smaller image size)
  output: 'standalone',

  reactCompiler: true,

  outputFileTracingRoot: path.join(__dirname),
  turbopack: {
    root: path.join(__dirname),
  },
};

export default nextConfig;
