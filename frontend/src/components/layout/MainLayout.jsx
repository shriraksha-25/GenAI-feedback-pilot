import React, { useState } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';

// Page titles and context descriptions map
const routeMeta = {
  '/': {
    title: 'Dashboard',
    description: "Here's what's happening with your customer feedback.",
  },
  '/feedback': {
    title: 'Customer Feedback',
    description: 'Collect customer feedback and send it for AI-powered analysis.',
  },
  '/insights': {
    title: 'Customer Insights',
    description: 'Understand what customers are saying and identify product opportunities.',
  },
  '/planning': {
    title: 'Product Planning',
    description: 'Convert AI-extracted insights into structured product initiatives and roadmap plans.',
  },
  '/requirements': {
    title: 'Requirements Management',
    description: 'Generate, refine, and track engineering requirements derived from customer pain points.',
  },
};

export default function MainLayout() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const location = useLocation();

  const currentMeta = routeMeta[location.pathname] || {
    title: 'FeedbackForge AI',
    description: 'Turn Customer Feedback into Product Decisions.',
  };

  return (
    <div className="min-h-screen bg-canvas flex flex-col">
      {/* Sidebar navigation */}
      <Sidebar isOpen={sidebarOpen} onClose={() => setSidebarOpen(false)} />

      {/* Main content wrapper shifted by sidebar width on desktop */}
      <div className="lg:pl-64 flex flex-col flex-1 min-w-0">
        <Header
          title={currentMeta.title}
          description={currentMeta.description}
          onMenuClick={() => setSidebarOpen(true)}
        />

        <main className="flex-1 p-4 sm:p-6 lg:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
