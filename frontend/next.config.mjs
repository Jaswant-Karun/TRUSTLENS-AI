/** @type {import('next').NextConfig} */
const isCapacitorBuild = process.env.CAPACITOR_BUILD === "true";

const nextConfig = {
  reactStrictMode: true,
  output: isCapacitorBuild ? "export" : "standalone",
  trailingSlash: isCapacitorBuild,
  images: isCapacitorBuild ? { unoptimized: true } : undefined,
  staticPageGenerationTimeout: 120,
  ...(!isCapacitorBuild
    ? {
        async rewrites() {
          const backendBase = process.env.BACKEND_API_URL || "http://127.0.0.1:8000";
          return [
            {
              source: "/api/v1/:path*",
              destination: `${backendBase}/api/v1/:path*`,
            },
          ];
        },
      }
    : {}),
};

export default nextConfig;
