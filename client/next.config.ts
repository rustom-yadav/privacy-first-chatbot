import type { NextConfig } from 'next';

const nextConfig: NextConfig = {
  // Enables standalone output for Docker (smaller image size)
  output: 'standalone',

  reactCompiler: true,
};

export default nextConfig;
