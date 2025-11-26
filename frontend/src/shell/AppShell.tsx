import { Outlet, NavLink } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetHeader, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Toaster } from "@/components/ui/sonner";
import { Menu, BarChart2, FileText, Users, MessageSquare, Settings } from "lucide-react";
import { useState } from "react";

export default function AppShell() {
  const [open, setOpen] = useState(false);
  const nav = [
    { to: "/", label: "Dashboard", icon: <BarChart2 className="h-4 w-4" /> },
    { to: "/jobs", label: "Jobs", icon: <FileText className="h-4 w-4" /> },
    { to: "/candidates", label: "Candidates", icon: <Users className="h-4 w-4" /> },
    { to: "/interviews", label: "Interviews", icon: <MessageSquare className="h-4 w-4" /> },
    // { to: "/settings", label: "Settings", icon: <Settings className="h-4 w-4" /> },
  ];
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-white text-gray-900">
      <div className="h-16 sticky top-0 z-20 bg-primary text-white backdrop-blur border-b flex items-center px-4 gap-3">
        <Button variant="ghost" size="icon" className="md:hidden" onClick={() => setOpen(true)}>
          <Menu className="h-5 w-5" />
        </Button>
        <div className="font-semibold">AI SMS Interview — Admin</div>
      </div>
      <div className="flex">
        <aside className="hidden md:flex md:flex-col md:w-64 border-r bg-[#0a1d2c] text-[#ffffff]">
          <div className="h-16 flex items-center px-6 font-semibold tracking-tight">AI SMS Interview</div>
          <nav className="flex-1 p-2 space-y-1">
            {nav.map((n) => (
              <NavLink key={n.to} to={n.to} end className={({isActive}) => 
                `w-full flex items-center gap-3 px-4 py-2 rounded-xl hover:bg-gray-500 ${isActive ? "bg-gray-500":""}`}>
                {n.icon}<span>{n.label}</span>
              </NavLink>
            ))}
          </nav>
          <div className="p-4 text-xs text-gray-500">© {new Date().getFullYear()} Your Org</div>
        </aside>

        <Sheet open={open} onOpenChange={setOpen}>
          <SheetTrigger asChild><div /></SheetTrigger>
          <SheetContent side="left" className="p-0 w-72">
            <SheetHeader className="px-6 py-4"><SheetTitle>AI SMS Interview</SheetTitle></SheetHeader>
            <nav className="p-2 space-y-1">
              {nav.map((n) => (
                <NavLink key={n.to} to={n.to} end onClick={()=>setOpen(false)} 
                  className={({isActive}) => `block px-4 py-2 rounded-xl hover:bg-gray-100 ${isActive?"bg-gray-100":""}`}>
                  {n.label}
                </NavLink>
              ))}
            </nav>
          </SheetContent>
        </Sheet>

        <main className="flex-1 p-4 md:p-6">
          <Outlet />
        </main>
      </div>
      <Toaster position="bottom-right" />
    </div>
  );
}
