import NextAuth, { type NextAuthOptions } from "next-auth";

const DJANGO_API_URL =
  process.env.DJANGO_API_URL || "http://localhost:8000";

export const authOptions: NextAuthOptions = {
  providers: [
    {
      id: "spotify",
      name: "Spotify",
      type: "oauth",
      authorization: {
        url: "https://accounts.spotify.com/authorize",
        params: {
          scope:
            "user-read-recently-played user-read-email user-read-private",
        },
      },
      token: "https://accounts.spotify.com/api/token",
      userinfo: "https://api.spotify.com/v1/me",
      clientId: process.env.SPOTIFY_CLIENT_ID!,
      checks: ["pkce", "state"],
      client: {
        token_endpoint_auth_method: "none",
      },
      profile(profile) {
        return {
          id: profile.id,
          name: profile.display_name,
          email: profile.email,
          image: profile.images?.[0]?.url,
        };
      },
    },
  ],
  callbacks: {
    async jwt({ token, account }) {
      if (account) {
        token.spotifyAccessToken = account.access_token;
        token.spotifyRefreshToken = account.refresh_token;
        token.spotifyExpiresAt = account.expires_at;

        try {
          const res = await fetch(`${DJANGO_API_URL}/api/auth/sync/`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              access_token: account.access_token,
              refresh_token: account.refresh_token,
              expires_at: account.expires_at,
            }),
          });

          if (res.ok) {
            const data = await res.json();
            token.djangoToken = data.token;
            token.userId = data.user_id;
            token.spotifyId = data.spotify_id;
          } else {
            console.error(
              "Django sync failed:",
              res.status,
              await res.text()
            );
          }
        } catch (error) {
          console.error("Failed to sync with Django backend:", error);
        }
      }

      return token;
    },
    async session({ session, token }) {
      session.djangoToken = token.djangoToken;
      session.userId = token.userId;
      session.spotifyId = token.spotifyId;
      return session;
    },
  },
  pages: {
    signIn: "/login",
  },
};

const handler = NextAuth(authOptions);
export { handler as GET, handler as POST };
