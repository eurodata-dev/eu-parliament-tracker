import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  poweredByHeader: false,
  images: {
    remotePatterns: [{ protocol: "https", hostname: "howtheyvote.eu", pathname: "/files/**" }],
  },
};

export default nextConfig;
