import { Outlet, Link } from "react-router-dom";

export default function PublicLayout() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white">
      <header className="h-14 bg-white border-b flex items-center px-4 justify-between">
        <Link to="/jobs" className="font-semibold">AI SMS Interview — Careers</Link>
        <nav className="text-sm">
          <Link to="/jobs" className="hover:underline">Jobs</Link>
        </nav>
      </header>
      <main className="max-w-5xl mx-auto p-4 md:p-6">
        <Outlet />
      </main>
      <footer className="py-8 text-center text-xs text-gray-500">© {new Date().getFullYear()} Your Org</footer>
    </div>
  );
}
