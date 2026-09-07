import type {NextConfig} from "next";

const nextConfig: NextConfig = {
  // Enables standalone output for Docker (smaller image size)
  output: "standalone",

  reactCompiler: true,

  // We use src/proxy.ts for dynamic API proxying at runtime
};

export default nextConfig;
