import {
  BarChart3,
  ClipboardList,
  FileText,
  LayoutDashboard,
  MessageSquare,
  Settings,
} from "lucide-react";
import { NavLink } from "react-router-dom";

function Sidebar() {
  const navigation = [
    {
      name: "Dashboard",
      path: "/",
      icon: LayoutDashboard,
    },
    {
      name: "Customer Feedback",
      path: "/feedback",
      icon: MessageSquare,
    },
    {
      name: "AI Insights",
      path: "/insights",
      icon: BarChart3,
    },
    {
      name: "Planning",
      path: "/planning",
      icon: ClipboardList,
    },
    {
      name: "Requirements",
      path: "/requirements",
      icon: FileText,
    },
  ];

  return (
    <aside className="fixed inset-y-0 left-0 z-40 flex w-64 flex-col border-r border-slate-200 bg-white">

      {/* =========================================
          LOGO / PRODUCT NAME
      ========================================== */}

      <div className="flex h-20 items-center border-b border-slate-100 px-6">

        <div>
          <h1 className="text-base font-semibold tracking-tight text-slate-900">
            ProductIQ
          </h1>

          <p className="mt-0.5 text-[10px] font-medium uppercase tracking-wider text-slate-400">
            Product Workspace
          </p>
        </div>

      </div>


      {/* =========================================
          NAVIGATION
      ========================================== */}

      <div className="flex-1 px-4 py-6">

        <p className="mb-3 px-3 text-[10px] font-semibold uppercase tracking-wider text-slate-400">
          Workspace
        </p>

        <nav className="space-y-1">

          {navigation.map((item) => {
            const Icon = item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                end={item.path === "/"}
                className={({ isActive }) =>
                  `group flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
                    isActive
                      ? "bg-blue-50 text-blue-700"
                      : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
                  }`
                }
              >
                {({ isActive }) => (
                  <>
                    <Icon
                      size={17}
                      className={
                        isActive
                          ? "text-blue-600"
                          : "text-slate-400 group-hover:text-slate-600"
                      }
                    />

                    <span>{item.name}</span>
                  </>
                )}
              </NavLink>
            );
          })}

        </nav>

      </div>


      {/* =========================================
          BOTTOM SECTION
      ========================================== */}

      <div className="border-t border-slate-100 p-4">

        {/* Settings */}

        <NavLink
          to="/settings"
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition ${
              isActive
                ? "bg-blue-50 text-blue-700"
                : "text-slate-500 hover:bg-slate-50 hover:text-slate-800"
            }`
          }
        >
          {({ isActive }) => (
            <>
              <Settings
                size={17}
                className={
                  isActive
                    ? "text-blue-600"
                    : "text-slate-400"
                }
              />

              <span>Settings</span>
            </>
          )}
        </NavLink>


        {/* User */}

        <div className="mt-4 flex items-center gap-3 border-t border-slate-100 pt-4">

          <div className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-200 text-xs font-semibold text-slate-600">
            U
          </div>

          <div className="min-w-0">

            <p className="truncate text-xs font-medium text-slate-800">
              User
            </p>

            <p className="truncate text-[10px] text-slate-400">
              Product Workspace
            </p>

          </div>

        </div>

      </div>

    </aside>
  );
}

export default Sidebar;