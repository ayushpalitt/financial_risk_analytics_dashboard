import { NextResponse } from "next/server";

const API_BASE_URL =
  process.env.BACKEND_API_BASE_URL ??
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "http://127.0.0.1:8001";

export async function POST(request: Request) {
  const body = await request.text();
  const response = await fetch(`${API_BASE_URL}/ai/report`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body,
    cache: "no-store",
  });

  const payload = await response.text();
  return new NextResponse(payload, {
    status: response.status,
    headers: {
      "Content-Type": response.headers.get("Content-Type") ?? "application/json",
    },
  });
}
