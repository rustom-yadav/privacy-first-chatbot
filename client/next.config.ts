import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Enables standalone output for Docker (smaller image size)
  output: "standalone",

  // Proxy API calls to the backend to avoid CORS issues in development
  async rewrites() {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    return [
      {
        source: "/api/:path*",
        destination: `${apiUrl}/api/:path*`,
      },
      {
        source: "/health",
        destination: `${apiUrl}/health`,
      },
    ];
  },
};

export default nextConfig;
