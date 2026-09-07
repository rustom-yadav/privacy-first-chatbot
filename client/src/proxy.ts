import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function proxy(request: NextRequest) {
  const { pathname, search } = request.nextUrl;

  if (pathname.startsWith("/api/") || pathname === "/health") {
    // Read the BACKEND_API_URL at runtime
    const apiUrl = process.env.BACKEND_API_URL || "http://localhost:8000";
    
    // Construct the destination URL
    const destinationUrl = new URL(pathname + search, apiUrl);
    
    // Proxy the request dynamically
    return NextResponse.rewrite(destinationUrl);
  }

  return NextResponse.next();
}

export const config = {
  matcher: ["/api/:path*", "/health"],
};
