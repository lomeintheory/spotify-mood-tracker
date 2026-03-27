"use client";

import { signIn } from "next-auth/react";

export default function LoginPage() {
  return (
    <div className="flex flex-col items-center justify-center min-h-screen">
      <button
        onClick={() => signIn("spotify", { callbackUrl: "/" })}
        className="border border-gray-600 cursor-pointer rounded-2xl p-1.5 bg-green-500 text-white hover:bg-green-600"
      >
        Sign in with Spotify
      </button>
    </div>
  );
}