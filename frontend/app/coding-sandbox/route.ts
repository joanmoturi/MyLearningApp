import { CODING_FRAME } from "../../lib/coding-runner";

export function GET() {
  return new Response(CODING_FRAME, {
    headers: {
      "Content-Type": "text/html; charset=utf-8",
      "Cache-Control": "no-store",
    },
  });
}
