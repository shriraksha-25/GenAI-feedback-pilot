import { Bell, Search } from "lucide-react";

function Header() {
  return (
    <header className="sticky top-0 z-30 h-20 border-b border-slate-200 bg-white">

      <div className="flex h-full items-center justify-between px-6 sm:px-8">

        {/* =========================================
            SEARCH
        ========================================== */}

        <div className="relative w-full max-w-md">

          <Search
            size={16}
            className="absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
          />

          <input
            type="text"
            placeholder="Search..."
            className="h-10 w-full rounded-lg border border-slate-200 bg-slate-50 pl-10 pr-4 text-sm text-slate-700 outline-none transition placeholder:text-slate-400 focus:border-blue-400 focus:bg-white focus:ring-2 focus:ring-blue-50"
          />

        </div>


        {/* =========================================
            RIGHT SIDE
        ========================================== */}

        <div className="ml-6 flex items-center gap-3">

          {/* Notification */}

          <button
            type="button"
            className="relative flex h-9 w-9 items-center justify-center rounded-lg text-slate-500 transition hover:bg-slate-50 hover:text-slate-800"
            aria-label="Notifications"
          >

            <Bell size={17} />

            {/* Notification indicator */}

            <span className="absolute right-2 top-2 h-1.5 w-1.5 rounded-full bg-blue-600 ring-2 ring-white" />

          </button>


          {/* Divider */}

          <div className="h-7 w-px bg-slate-200" />


          {/* User */}

          <div className="flex items-center gap-3">

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-blue-600 text-xs font-semibold text-white">
              U
            </div>

            <div className="hidden sm:block">

              <p className="text-xs font-semibold text-slate-800">
                User
              </p>

              <p className="text-[10px] text-slate-400">
                Product Workspace
              </p>

            </div>

          </div>

        </div>

      </div>

    </header>
  );
}

export default Header;