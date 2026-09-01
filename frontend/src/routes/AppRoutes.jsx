import { BrowserRouter, Routes, Route } from "react-router-dom";

import MainLayout from "../components/layout/MainLayout";
import Dashboard from "../pages/Dashboard";
import CustomerFeedback from "../pages/CustomerFeedback";

function Placeholder({ title, description }) {
  return (
    <div className="mx-auto max-w-7xl">

      <div className="mb-8">
        <p className="mb-2 text-sm font-medium text-gray-500">
          Product Workspace
        </p>

        <h2 className="text-3xl font-bold tracking-tight text-gray-900">
          {title}
        </h2>

        <p className="mt-2 text-sm text-gray-500">
          {description}
        </p>
      </div>

      <div className="rounded-xl border border-gray-200 bg-white p-12 text-center">
        <p className="text-sm text-gray-500">
          This workspace will be developed in the next phase.
        </p>
      </div>

    </div>
  );
}

function AppRoutes() {
  return (
    <BrowserRouter>
      <MainLayout>
        <Routes>

          {/* Dashboard */}
          <Route
            path="/"
            element={<Dashboard />}
          />

          {/* Customer Feedback */}
          <Route
            path="/feedback"
            element={<CustomerFeedback />}
          />

          {/* AI Insights */}
          <Route
            path="/insights"
            element={
              <Placeholder
                title="AI Insights"
                description="Explore AI-generated product insights."
              />
            }
          />

          {/* Planning */}
          <Route
            path="/planning"
            element={
              <Placeholder
                title="Planning"
                description="Turn insights into actionable product plans."
              />
            }
          />

          {/* Requirements */}
          <Route
            path="/requirements"
            element={
              <Placeholder
                title="Requirements"
                description="Generate and manage product requirements."
              />
            }
          />

          {/* Settings */}
          <Route
            path="/settings"
            element={
              <Placeholder
                title="Settings"
                description="Manage your product workspace."
              />
            }
          />

        </Routes>
      </MainLayout>
    </BrowserRouter>
  );
}

export default AppRoutes;