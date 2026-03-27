'use client';

import { signOut } from "next-auth/react";

export default function LogoutButton() {
  return (
    <div>
      <button 
        onClick={() => signOut({ callbackUrl: '/login' })}
        className="border border-gray-500 rounded-xl p-2 cursor-pointer"
      >
        Sign Out
      </button>
    </div>
  )
}