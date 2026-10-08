import type { MetadataRoute } from "next";
import { SITE_URL } from "@/lib/mail";

export default function robots(): MetadataRoute.Robots {
  return {
    rules: { userAgent: "*", allow: "/", disallow: ["/api/", "/unsubscribe"] },
    sitemap: `${SITE_URL}/sitemap.xml`,
  };
}
