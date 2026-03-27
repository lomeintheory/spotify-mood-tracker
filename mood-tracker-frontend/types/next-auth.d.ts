import { DefaultSession } from "next-auth";

declare module "next-auth" {
  interface Session extends DefaultSession {
    djangoToken?: string;
    userId?: number;
    spotifyId?: string;
  }
}

declare module "next-auth/jwt" {
  interface JWT {
    djangoToken?: string;
    userId?: number;
    spotifyId?: string;
    spotifyAccessToken?: string;
    spotifyRefreshToken?: string;
    spotifyExpiresAt?: number;
  }
}
