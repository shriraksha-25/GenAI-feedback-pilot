import Sidebar from "./Sidebar";
import Header from "./Header";

function MainLayout({ children }) {
  return (
    <div className="min-h-screen bg-slate-50">

      {/* Sidebar */}

      <Sidebar />

      {/* Main content area */}

      <div className="min-h-screen pl-64">

        {/* Header */}

        <Header />

        {/* Page content */}

        <main className="px-6 py-6 sm:px-8 sm:py-8">
          {children}
        </main>

      </div>

    </div>
  );
}

export default MainLayout;