import LogoutButton from "@/src/components/logout-button";

export default function CalendarLayout({ children } : Readonly<{children: React.ReactNode}>) {
  return (
    <div>
      <nav className="flex flex-row justify-between p-2">
        <h1>My Calendar</h1>
        <LogoutButton />
      </nav>
      <main>
        {children}
      </main>
    </div>
  )
}