import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import Button from '../components/common/Button';
import {
  Compass,
  ArrowRight,
  Sparkles,
  MessageSquareQuote,
  AlertTriangle,
  Lightbulb,
  Layers,
  KanbanSquare,
  FileText,
  CheckCircle2,
  Check,
  ChevronRight,
  ShieldCheck,
  TrendingUp,
  Cpu,
  BarChart3,
  Users,
  Zap,
  Clock,
  ArrowUpRight,
  FileSpreadsheet,
  ChevronDown,
  ChevronUp,
  Star,
  ExternalLink,
  Sliders,
} from 'lucide-react';

export default function LandingPage() {
  const { isAuthenticated, user } = useAuth();
  const navigate = useNavigate();

  // Interactive Live Demo Sandbox state
  const [activeTab, setActiveTab] = useState('clustering');
  const [activeScenario, setActiveScenario] = useState('checkout');
  const [openFaqIndex, setOpenFaqIndex] = useState(0);

  // ROI Calculator state
  const [feedbackVolume, setFeedbackVolume] = useState(250);
  const [teamSize, setTeamSize] = useState(5);

  // Scenarios data for the live interactive sandbox
  const scenarios = {
    checkout: {
      name: 'Stripe 3DS Checkout Dropoff',
      channel: 'Zendesk & Intercom',
      sampleFeedback: [
        '"EU customers are getting card decline error 4002 when 3D Secure modal times out on Firefox."',
        '"Cannot complete $5k annual billing checkout - bank authorization page fails to redirect back."',
        '"Lost our entire enterprise purchase attempt because the card billing address field refused postal codes."',
      ],
      aiSummary: 'Critical payment friction identified affecting European enterprise accounts during 3D Secure authorization. High revenue at risk ($14,200 estimated ARR).',
      issues: [
        { title: 'Firefox 3DS Redirect Timeout', severity: 'High', freq: 42, impact: 'High ARR' },
        { title: 'EU Postal Code Validation Regex Error', severity: 'Medium', freq: 19, impact: 'Medium ARR' },
      ],
      opportunity: 'Implement Fallback Hosted Invoice Checkout with asynchronous 3DS validation.',
      prdPreview: {
        title: 'PRD: Resilient 3DS Payment Flow & Address Auto-format',
        userStory: 'As an international customer, I want seamless 3D Secure verification so that my annual subscription payment processes without dropoff.',
        acceptanceCriteria: [
          'Verify Firefox redirect handles postMessage callback within 15s window',
          'Support international postal codes up to 12 alphanumeric characters',
          'Trigger fallback invoice email when 3DS session encounters bank API downtime',
        ],
      },
    },
    mobile: {
      name: 'Mobile App Sync & Offline Mode',
      channel: 'App Store & In-App NPS',
      sampleFeedback: [
        '"Whenever I fly and lose signal, all my drafts disappear when I reconnect to WiFi."',
        '"App drains 35% battery in 20 minutes when syncing background customer profiles."',
        '"Offline edits conflict and overwrite existing team member notes without warning."',
      ],
      aiSummary: 'Data integrity and battery consumption issues reported by mobile road-warriors. Heavy background polling without delta compression causing sync conflicts.',
      issues: [
        { title: 'Draft Overwrite on Reconnect', severity: 'High', freq: 67, impact: 'Retention Risk' },
        { title: 'Excessive Background Battery Consumption', severity: 'Medium', freq: 38, impact: 'CSAT Drop' },
      ],
      opportunity: 'Implement CRDT-based local SQLite caching with delta sync and exponential backoff.',
      prdPreview: {
        title: 'PRD: Offline-First Conflict-Free Note Replication',
        userStory: 'As a mobile user, I want my notes saved locally offline so that I never lose edits when reconnecting to unstable network connections.',
        acceptanceCriteria: [
          'Store all edits in local SQLite before attempting network synchronization',
          'Use field-level timestamps to merge concurrent updates without data destruction',
          'Limit background polling to exponential backoff when battery < 20%',
        ],
      },
    },
    sso: {
      name: 'Enterprise SAML / Okta Integration',
      channel: 'Sales Calls & Gong Transcripts',
      sampleFeedback: [
        '"Deal stalled: Security team at Fortune 500 prospect requires Okta SCIM directory provisioning."',
        '"We cannot manually onboard 300 engineers every quarter; need automated Just-in-Time SAML 2.0."',
        '"Audit log export in CSV or Splunk webhook is a mandatory compliance requirement for Q3."',
      ],
      aiSummary: 'Three enterprise deals ($180k pipeline) blocked on identity management compliance. Priority need for SAML 2.0 and automated role-based SCIM provisioning.',
      issues: [
        { title: 'Missing SCIM 2.0 User Sync', severity: 'High', freq: 14, impact: '$180k Pipeline' },
        { title: 'Manual SAML Metadata Upload Friction', severity: 'Medium', freq: 8, impact: 'Sales Cycle' },
      ],
      opportunity: 'Deliver turnkey WorkOS/Okta enterprise SSO with role mapping & automated provisioning.',
      prdPreview: {
        title: 'PRD: Enterprise SCIM & SAML 2.0 Identity Provider Bridge',
        userStory: 'As an enterprise IT administrator, I want to provision user accounts through Okta/Azure AD so that access governance adheres to SOC2 compliance.',
        acceptanceCriteria: [
          'Support SAML 2.0 metadata XML upload and ACS endpoint verification',
          'Implement SCIM /Users and /Groups REST endpoints with bearer token auth',
          'Audit log every role escalation and de-provisioning event with 365-day retention',
        ],
      },
    },
  };

  const currentScenario = scenarios[activeScenario];

  // ROI calculations
  const hoursSavedPerWeek = Math.round((feedbackVolume * 0.12) + (teamSize * 2.5));
  const estimatedAnnualSavings = Math.round(hoursSavedPerWeek * 52 * 75); // $75/hr average PM cost

  const faqs = [
    {
      q: 'How does FeedbackForge AI ingest customer feedback?',
      a: 'FeedbackForge accepts customer feedback through direct text input and file uploads (.CSV, .TXT, .PDF, .DOC, .DOCX). You can import customer support tickets, NPS comments, user interview transcripts, sales call notes, and App Store reviews in seconds.',
    },
    {
      q: 'Does it replace our existing project management tools like Linear or Jira?',
      a: 'No, FeedbackForge enhances them! FeedbackForge is the intelligence workspace that sits between your raw customer feedback channels and your engineering backlog. It extracts issues, themes, and priorities, generates complete PRDs with user stories and acceptance criteria, which you can easily push to Jira, Linear, or GitHub.',
    },
    {
      q: 'How does the AI determine issue severity and priority?',
      a: 'Our AI pipeline analyzes semantic patterns, frequency counts, sentiment intensity, and customer revenue impact indicators. It groups isolated complaints into quantified problem clusters so you know exactly which bugs or features will move the needle most.',
    },
    {
      q: 'Is our customer voice data secure and private?',
      a: 'Yes. FeedbackForge uses encrypted data transmission (HTTPS/TLS) and isolated local/cloud storage. Your proprietary customer feedback is never used to train public foundation models, ensuring complete confidentiality for B2B and consumer data alike.',
    },
    {
      q: 'Can I test FeedbackForge without entering credit card information?',
      a: 'Absolutely. You can create a free account immediately with full access to feedback ingestion, AI clustering, planning boards, and PRD generation. No credit card is required.',
    },
  ];

  return (
    <div className="min-h-screen bg-canvas text-slate-800 selection:bg-emerald-100 selection:text-emerald-900">
      {/* Top Banner for Logged-In Users */}
      {isAuthenticated && (
        <div className="bg-emerald-900 text-emerald-100 px-4 py-2.5 text-xs font-medium flex items-center justify-between border-b border-emerald-800">
          <div className="flex items-center gap-2 max-w-7xl mx-auto w-full justify-between">
            <span className="flex items-center gap-1.5 truncate">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse"></span>
              Logged in as <strong className="text-white">{user?.name || user?.email}</strong>. Ready to work on your product intelligence?
            </span>
            <Link
              to="/dashboard"
              className="inline-flex items-center gap-1 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-semibold px-3 py-1 rounded text-xs transition-colors shadow-sm flex-shrink-0"
            >
              Open Workspace <ArrowRight className="w-3.5 h-3.5" />
            </Link>
          </div>
        </div>
      )}

      {/* Sticky Top Navigation */}
      <nav className="sticky top-0 z-40 bg-white/95 backdrop-blur-md border-b border-slate-200/80 transition-all">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between gap-4">
          {/* Brand Logo */}
          <Link to="/" className="flex items-center gap-2.5 group">
            <div className="w-9 h-9 rounded-lg bg-emerald-600 flex items-center justify-center text-white shadow-sm group-hover:bg-emerald-700 transition-colors">
              <Compass className="w-5 h-5 transition-transform group-hover:rotate-45" />
            </div>
            <div className="flex flex-col">
              <span className="text-base font-bold text-slate-900 tracking-tight leading-none">
                FeedbackForge<span className="text-emerald-600 font-extrabold ml-0.5">AI</span>
              </span>
              <span className="text-[10px] text-slate-500 font-semibold uppercase tracking-wider mt-0.5">
                Product Intelligence Workspace
              </span>
            </div>
          </Link>

          {/* Navigation Links (Desktop) */}
          <div className="hidden md:flex items-center gap-7 text-xs font-medium text-slate-600">
            <a href="#features" className="hover:text-emerald-600 transition-colors">
              Features
            </a>
            <a href="#interactive-demo" className="hover:text-emerald-600 transition-colors flex items-center gap-1">
              Live Demo
              <span className="bg-emerald-100 text-emerald-800 text-[9px] font-bold px-1.5 py-0.5 rounded-full">Interactive</span>
            </a>
            <a href="#how-it-works" className="hover:text-emerald-600 transition-colors">
              How It Works
            </a>
            <a href="#roi-calculator" className="hover:text-emerald-600 transition-colors">
              ROI Calculator
            </a>
            <a href="#faq" className="hover:text-emerald-600 transition-colors">
              FAQ
            </a>
          </div>

          {/* Action CTAs */}
          <div className="flex items-center gap-3">
            {isAuthenticated ? (
              <Link to="/dashboard">
                <Button variant="primary" size="sm" icon={ArrowRight}>
                  Go to Dashboard
                </Button>
              </Link>
            ) : (
              <>
                <Link
                  to="/login"
                  className="text-xs font-semibold text-slate-700 hover:text-emerald-600 px-3 py-2 transition-colors"
                >
                  Sign In
                </Link>
                <Link to="/register">
                  <Button variant="primary" size="sm" icon={ArrowRight}>
                    Get Started Free
                  </Button>
                </Link>
              </>
            )}
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-20 md:pt-20 md:pb-28 border-b border-slate-200/60 bg-gradient-to-b from-white via-canvas to-canvas">
        {/* Subtle grid pattern background */}
        <div className="absolute inset-0 bg-[linear-gradient(to_right,#f1f5f9_1px,transparent_1px),linear-gradient(to_bottom,#f1f5f9_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] pointer-events-none" />

        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          {/* Pill Badge */}
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-800 text-xs font-semibold mb-6 shadow-xs animate-fade-in">
            <Sparkles className="w-3.5 h-3.5 text-emerald-600 animate-spin" style={{ animationDuration: '4s' }} />
            <span>Product Intelligence Workspace 2.0</span>
            <span className="w-1 h-1 rounded-full bg-emerald-400" />
            <span className="text-emerald-700 font-medium">Turn Voice of Customer into Roadmaps</span>
          </div>

          {/* Primary Headline */}
          <h1 className="text-3xl sm:text-5xl lg:text-6xl font-extrabold text-slate-950 tracking-tight leading-[1.12] max-w-4xl mx-auto">
            Turn customer feedback into{' '}
            <span className="text-emerald-600 bg-gradient-to-r from-emerald-600 via-emerald-700 to-teal-700 bg-clip-text text-transparent">
              validated product decisions.
            </span>
          </h1>

          {/* Subheading */}
          <p className="mt-6 text-base sm:text-lg text-slate-600 max-w-2xl mx-auto leading-relaxed">
            Stop losing hours reading through support tickets, Discord pings, and survey exports.
            FeedbackForge AI ingests raw customer voice, surfaces root issues, prioritizes opportunities,
            and writes engineering-ready PRDs in seconds.
          </p>

          {/* CTAs */}
          <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-3.5 max-w-md mx-auto">
            <Link to="/register" className="w-full sm:w-auto">
              <Button
                variant="primary"
                size="lg"
                icon={ArrowRight}
                className="w-full sm:w-auto text-sm px-7 py-3 shadow-sm hover:shadow transition-all"
              >
                Start Free Trial
              </Button>
            </Link>
            <a href="#interactive-demo" className="w-full sm:w-auto">
              <Button
                variant="outline"
                size="lg"
                icon={Zap}
                className="w-full sm:w-auto text-sm px-6 py-3 bg-white"
              >
                Try Interactive Demo
              </Button>
            </a>
          </div>

          {/* Trust Guarantees */}
          <div className="mt-8 flex flex-wrap items-center justify-center gap-x-6 gap-y-2 text-xs text-slate-500 font-medium">
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> No credit card required
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Instant CSV & PDF import
            </span>
            <span className="flex items-center gap-1.5">
              <CheckCircle2 className="w-4 h-4 text-emerald-600" /> Production-ready PRD output
            </span>
          </div>

          {/* Hero Workspace Snapshot Mockup */}
          <div className="mt-12 relative max-w-5xl mx-auto">
            <div className="rounded-xl border border-slate-200 bg-white shadow-xl overflow-hidden text-left">
              {/* Fake Window Chrome */}
              <div className="bg-slate-100 border-b border-slate-200 px-4 py-3 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 rounded-full bg-rose-400"></div>
                  <div className="w-3 h-3 rounded-full bg-amber-400"></div>
                  <div className="w-3 h-3 rounded-full bg-emerald-400"></div>
                  <span className="ml-2 text-xs font-mono text-slate-500">
                    feedbackforge-workspace // executive-overview
                  </span>
                </div>
                <div className="flex items-center gap-2 text-xs text-slate-500">
                  <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
                  AI Analysis Engine Active
                </div>
              </div>

              {/* Preview Dashboard Content */}
              <div className="p-6 bg-canvas-subtle/40 space-y-6">
                {/* 4 Quick Stat Metric Tiles */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Feedback Ingested</span>
                    <div className="text-xl font-bold text-slate-900 mt-1 flex items-baseline gap-1.5">
                      1,482 <span className="text-[11px] text-emerald-600 font-medium">+18% this wk</span>
                    </div>
                  </div>
                  <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Friction Issues</span>
                    <div className="text-xl font-bold text-slate-900 mt-1 flex items-baseline gap-1.5">
                      38 <span className="text-[11px] text-rose-600 font-medium">8 critical</span>
                    </div>
                  </div>
                  <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Feature Requests</span>
                    <div className="text-xl font-bold text-slate-900 mt-1 flex items-baseline gap-1.5">
                      94 <span className="text-[11px] text-slate-500 font-normal">clustered</span>
                    </div>
                  </div>
                  <div className="bg-white p-3.5 rounded-lg border border-slate-200 shadow-xs">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider block">Roadmap Initiatives</span>
                    <div className="text-xl font-bold text-slate-900 mt-1 flex items-baseline gap-1.5">
                      12 <span className="text-[11px] text-violet-600 font-medium">PRDs Ready</span>
                    </div>
                  </div>
                </div>

                {/* AI Executive Insight Card */}
                <div className="bg-white p-4 rounded-lg border border-slate-200 shadow-subtle flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-violet-600" />
                      <span className="text-xs font-bold uppercase tracking-wider text-violet-700">
                        AI Executive Synthesis
                      </span>
                    </div>
                    <p className="text-xs text-slate-700 max-w-2xl leading-relaxed">
                      "Customer friction heavily concentrates on two bottlenecks: European payment authorization dropoffs (42 reports) and mobile background synchronization loss (67 reports). Addressing these two initiatives mitigates an estimated $32k in immediate monthly churn risk."
                    </p>
                  </div>
                  <div className="flex items-center gap-2 flex-shrink-0">
                    <Link to="/register">
                      <Button variant="primary" size="sm" icon={ChevronRight}>
                        Generate PRD
                      </Button>
                    </Link>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof Logos & Metrics */}
      <section className="py-10 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <p className="text-xs font-semibold uppercase tracking-wider text-slate-400 mb-6">
            Empowering modern product managers, founders, and engineering teams
          </p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 max-w-4xl mx-auto">
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-2xl font-bold text-slate-900">10x</span>
              <p className="text-xs text-slate-500 font-medium mt-1">Faster feedback triage</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-2xl font-bold text-emerald-700">84%</span>
              <p className="text-xs text-slate-500 font-medium mt-1">Reduction in PRD drafting time</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-2xl font-bold text-slate-900">100k+</span>
              <p className="text-xs text-slate-500 font-medium mt-1">Customer comments analyzed</p>
            </div>
            <div className="p-4 rounded-lg bg-slate-50 border border-slate-100">
              <span className="text-2xl font-bold text-violet-700">99.4%</span>
              <p className="text-xs text-slate-500 font-medium mt-1">Accurate theme clustering</p>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Live Demo Sandbox */}
      <section id="interactive-demo" className="py-16 md:py-24 bg-canvas border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
              Interactive Product Sandbox
            </span>
            <h2 className="mt-3 text-2xl sm:text-4xl font-extrabold text-slate-950 tracking-tight">
              Test FeedbackForge on real product scenarios
            </h2>
            <p className="mt-3 text-sm text-slate-600">
              Select a sample dataset below to see how raw customer comments transform into clustered issues,
              prioritized opportunities, and finalized technical requirements.
            </p>
          </div>

          {/* Scenario Selector Buttons */}
          <div className="flex flex-wrap items-center justify-center gap-2 mb-8">
            <button
              type="button"
              onClick={() => setActiveScenario('checkout')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
                activeScenario === 'checkout'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Zap className="w-3.5 h-3.5 text-amber-400" />
              Fintech: 3DS Checkout Dropoff
            </button>
            <button
              type="button"
              onClick={() => setActiveScenario('mobile')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
                activeScenario === 'mobile'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <Cpu className="w-3.5 h-3.5 text-emerald-400" />
              Mobile App: Offline Sync & Battery
            </button>
            <button
              type="button"
              onClick={() => setActiveScenario('sso')}
              className={`px-4 py-2 rounded-lg text-xs font-semibold transition-all flex items-center gap-2 ${
                activeScenario === 'sso'
                  ? 'bg-slate-900 text-white shadow-sm'
                  : 'bg-white text-slate-600 border border-slate-200 hover:bg-slate-50'
              }`}
            >
              <ShieldCheck className="w-3.5 h-3.5 text-violet-400" />
              B2B SaaS: Okta SAML & SCIM
            </button>
          </div>

          {/* Interactive Workspace Simulator Window */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-md overflow-hidden max-w-5xl mx-auto">
            {/* Top Toolbar Navigation */}
            <div className="bg-slate-50 border-b border-slate-200 px-6 py-3 flex flex-wrap items-center justify-between gap-3">
              <div className="flex items-center gap-2">
                <span className="w-2.5 h-2.5 rounded-full bg-emerald-500"></span>
                <span className="text-xs font-bold text-slate-800">
                  Active Scenario: {currentScenario.name}
                </span>
                <span className="text-[11px] bg-slate-200 text-slate-700 px-2 py-0.5 rounded font-mono">
                  Channel: {currentScenario.channel}
                </span>
              </div>

              {/* Step Navigation Tabs */}
              <div className="flex items-center gap-1 bg-slate-200/70 p-1 rounded-md">
                <button
                  type="button"
                  onClick={() => setActiveTab('clustering')}
                  className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                    activeTab === 'clustering'
                      ? 'bg-white text-slate-900 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  1. Ingestion & Analysis
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('planning')}
                  className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                    activeTab === 'planning'
                      ? 'bg-white text-slate-900 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  2. Priority Planning
                </button>
                <button
                  type="button"
                  onClick={() => setActiveTab('prd')}
                  className={`px-3 py-1 rounded text-xs font-medium transition-colors ${
                    activeTab === 'prd'
                      ? 'bg-white text-slate-900 shadow-xs font-semibold'
                      : 'text-slate-600 hover:text-slate-900'
                  }`}
                >
                  3. Generated PRD
                </button>
              </div>
            </div>

            {/* Tab 1: Ingestion & Analysis */}
            {activeTab === 'clustering' && (
              <div className="p-6 space-y-6">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Raw Ingested Customer Voices (Sample)
                  </h4>
                  <div className="space-y-2">
                    {currentScenario.sampleFeedback.map((text, idx) => (
                      <div
                        key={idx}
                        className="p-3 bg-slate-50 border border-slate-200 rounded-md text-xs text-slate-700 font-mono italic"
                      >
                        {text}
                      </div>
                    ))}
                  </div>
                </div>

                {/* AI Clustered Synthesis */}
                <div className="p-4 rounded-lg bg-emerald-50/70 border border-emerald-200 text-xs">
                  <div className="flex items-center gap-1.5 font-bold text-emerald-900 mb-1">
                    <Sparkles className="w-3.5 h-3.5 text-emerald-600" />
                    AI Synthesis & Root Cause
                  </div>
                  <p className="text-emerald-800 leading-relaxed">
                    {currentScenario.aiSummary}
                  </p>
                </div>

                {/* Detected Issues */}
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Extracted Friction Issues & Frequency
                  </h4>
                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                    {currentScenario.issues.map((issue, idx) => (
                      <div
                        key={idx}
                        className="p-3.5 rounded-lg border border-slate-200 bg-white shadow-xs flex items-center justify-between"
                      >
                        <div>
                          <p className="text-xs font-semibold text-slate-900">{issue.title}</p>
                          <span className="text-[11px] text-slate-500">
                            Impact: <strong className="text-rose-600">{issue.impact}</strong>
                          </span>
                        </div>
                        <div className="text-right">
                          <span className="text-xs font-bold text-slate-900 bg-slate-100 px-2 py-0.5 rounded">
                            {issue.freq} reports
                          </span>
                          <span className="block text-[10px] text-rose-600 font-semibold mt-0.5">
                            {issue.severity} Priority
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end pt-2">
                  <Button
                    variant="primary"
                    size="sm"
                    icon={ArrowRight}
                    onClick={() => setActiveTab('planning')}
                  >
                    Proceed to Planning Phase
                  </Button>
                </div>
              </div>
            )}

            {/* Tab 2: Priority Planning */}
            {activeTab === 'planning' && (
              <div className="p-6 space-y-6">
                <div>
                  <h4 className="text-xs font-bold uppercase tracking-wider text-slate-400 mb-2">
                    Actionable Opportunity Identified
                  </h4>
                  <div className="p-4 rounded-lg border border-emerald-200 bg-emerald-50/50">
                    <div className="flex items-center gap-2 text-xs font-bold text-emerald-900 mb-1">
                      <Lightbulb className="w-4 h-4 text-emerald-600" />
                      Strategic Solution Recommendation
                    </div>
                    <p className="text-xs text-slate-700 leading-relaxed font-medium">
                      {currentScenario.opportunity}
                    </p>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-center">
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                      Business Urgency
                    </span>
                    <p className="text-base font-bold text-rose-600 mt-1">High (P0)</p>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                      Customer Sentiment Score
                    </span>
                    <p className="text-base font-bold text-amber-600 mt-1">-0.68 Negative</p>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-50 border border-slate-200">
                    <span className="text-[11px] font-semibold text-slate-500 uppercase tracking-wider">
                      Suggested Sprint
                    </span>
                    <p className="text-base font-bold text-slate-900 mt-1">Current Sprint + 1</p>
                  </div>
                </div>

                <div className="flex justify-between pt-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setActiveTab('clustering')}
                  >
                    Back to Ingestion
                  </Button>
                  <Button
                    variant="primary"
                    size="sm"
                    icon={ArrowRight}
                    onClick={() => setActiveTab('prd')}
                  >
                    View Auto-Generated PRD
                  </Button>
                </div>
              </div>
            )}

            {/* Tab 3: Generated PRD */}
            {activeTab === 'prd' && (
              <div className="p-6 space-y-5">
                <div className="flex items-center justify-between pb-3 border-b border-slate-200">
                  <div className="flex items-center gap-2">
                    <FileText className="w-4 h-4 text-emerald-600" />
                    <h3 className="text-sm font-bold text-slate-900">
                      {currentScenario.prdPreview.title}
                    </h3>
                  </div>
                  <span className="text-[11px] bg-emerald-100 text-emerald-800 font-semibold px-2 py-0.5 rounded">
                    Engineered Specs
                  </span>
                </div>

                <div className="bg-slate-50 p-3.5 rounded-lg border border-slate-200 space-y-1">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    User Story
                  </span>
                  <p className="text-xs text-slate-800 font-medium">
                    {currentScenario.prdPreview.userStory}
                  </p>
                </div>

                <div className="space-y-2">
                  <span className="text-[11px] font-bold uppercase tracking-wider text-slate-500">
                    Acceptance Criteria (Gherkin-Ready)
                  </span>
                  <div className="space-y-1.5">
                    {currentScenario.prdPreview.acceptanceCriteria.map((crit, idx) => (
                      <div
                        key={idx}
                        className="flex items-start gap-2 text-xs text-slate-700 bg-white p-2.5 rounded border border-slate-200 shadow-xs"
                      >
                        <Check className="w-3.5 h-3.5 text-emerald-600 mt-0.5 flex-shrink-0" />
                        <span>{crit}</span>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="p-3 bg-violet-50 border border-violet-200 rounded-md flex items-center justify-between text-xs text-violet-800">
                  <span className="font-medium">
                    Ready to turn this into a live backlog ticket?
                  </span>
                  <Link to="/register">
                    <Button variant="primary" size="sm" icon={ExternalLink}>
                      Export to Jira / Linear
                    </Button>
                  </Link>
                </div>
              </div>
            )}
          </div>
        </div>
      </section>

      {/* 4 Core Pillars of FeedbackForge */}
      <section id="features" className="py-16 md:py-24 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
              Core Capabilities
            </span>
            <h2 className="mt-3 text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight">
              A comprehensive system for product intelligence
            </h2>
            <p className="mt-3 text-base text-slate-600">
              From raw unstructured customer messages to prioritized initiatives and engineering PRDs.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {/* Pillar 1 */}
            <div className="p-6 rounded-xl border border-slate-200 bg-canvas hover:border-emerald-300 transition-all hover:shadow-sm group">
              <div className="w-10 h-10 rounded-lg bg-emerald-100/80 text-emerald-700 flex items-center justify-center mb-4 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
                <MessageSquareQuote className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">
                1. Omni-channel Ingestion
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Upload CSVs, customer interview transcripts, PDFs, or submit feedback directly. Ingest support tickets and App Store reviews without manual reformatting.
              </p>
              <ul className="text-[11px] text-slate-500 space-y-1.5">
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Multi-file drag & drop (.csv, .pdf, .docx)
                </li>
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Auto-sanitizes raw text feeds
                </li>
              </ul>
            </div>

            {/* Pillar 2 */}
            <div className="p-6 rounded-xl border border-slate-200 bg-canvas hover:border-emerald-300 transition-all hover:shadow-sm group">
              <div className="w-10 h-10 rounded-lg bg-violet-100/80 text-violet-700 flex items-center justify-center mb-4 group-hover:bg-violet-600 group-hover:text-white transition-colors">
                <Sparkles className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">
                2. AI Friction Clustering
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Our NLP models group thousands of disparate comments into verified friction areas, extracting bug severity, sentiment score, and frequency metrics.
              </p>
              <ul className="text-[11px] text-slate-500 space-y-1.5">
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Frequency-weighted bug sorting
                </li>
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Automatic sentiment classification
                </li>
              </ul>
            </div>

            {/* Pillar 3 */}
            <div className="p-6 rounded-xl border border-slate-200 bg-canvas hover:border-emerald-300 transition-all hover:shadow-sm group">
              <div className="w-10 h-10 rounded-lg bg-amber-100/80 text-amber-700 flex items-center justify-center mb-4 group-hover:bg-amber-600 group-hover:text-white transition-colors">
                <KanbanSquare className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">
                3. Strategic Roadmap Board
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Convert clustered friction into prioritized product initiatives. Organize by Backlog, In Progress, and Completed with clear impact-vs-effort scoring.
              </p>
              <ul className="text-[11px] text-slate-500 space-y-1.5">
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Evidence-backed priority ranks
                </li>
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Direct link to customer quotes
                </li>
              </ul>
            </div>

            {/* Pillar 4 */}
            <div className="p-6 rounded-xl border border-slate-200 bg-canvas hover:border-emerald-300 transition-all hover:shadow-sm group">
              <div className="w-10 h-10 rounded-lg bg-teal-100/80 text-teal-700 flex items-center justify-center mb-4 group-hover:bg-teal-600 group-hover:text-white transition-colors">
                <FileText className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-slate-900 mb-2">
                4. Automated PRD Authoring
              </h3>
              <p className="text-xs text-slate-600 leading-relaxed mb-4">
                Generate production-ready specifications with one click. Get user stories, comprehensive acceptance criteria, edge case warnings, and technical notes.
              </p>
              <ul className="text-[11px] text-slate-500 space-y-1.5">
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Gherkin-compatible criteria
                </li>
                <li className="flex items-center gap-1.5">
                  <Check className="w-3.5 h-3.5 text-emerald-600" /> Instant copy to Linear / Jira
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Before vs After Section */}
      <section id="how-it-works" className="py-16 md:py-24 bg-canvas border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-500 bg-slate-100 px-3 py-1 rounded-full border border-slate-200">
              The Product Transformation
            </span>
            <h2 className="mt-3 text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight">
              Replace messy spreadsheets with an intelligence engine
            </h2>
            <p className="mt-3 text-base text-slate-600">
              See what happens when you upgrade your team's feedback triage workflow.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-5xl mx-auto">
            {/* The Old Way */}
            <div className="bg-white p-7 rounded-xl border border-rose-200 shadow-xs relative">
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-rose-700 bg-rose-50 px-2.5 py-1 rounded-full mb-4">
                <AlertTriangle className="w-3.5 h-3.5" />
                Without FeedbackForge (The Old Way)
              </div>
              <ul className="space-y-4 text-xs text-slate-600">
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✕</span>
                  <span><strong>Scattered Channels:</strong> Customer feedback is trapped across Zendesk, Slack, Gong, App Store, and random meeting notes.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✕</span>
                  <span><strong>Loudest Voice Bias:</strong> Roadmaps are steered by whichever customer complained most recently on an executive call.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✕</span>
                  <span><strong>Manual Spreadsheet Tagging:</strong> PMs waste 8+ hours a week manually copying rows into Google Sheets.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-rose-100 text-rose-600 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✕</span>
                  <span><strong>Vague Tickets:</strong> Engineers receive ambiguous tickets without clear acceptance criteria, leading to rework.</span>
                </li>
              </ul>
            </div>

            {/* The FeedbackForge Way */}
            <div className="bg-white p-7 rounded-xl border-2 border-emerald-500 shadow-md relative">
              <div className="inline-flex items-center gap-1.5 text-xs font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-full mb-4">
                <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
                With FeedbackForge AI (The Intelligent Way)
              </div>
              <ul className="space-y-4 text-xs text-slate-700">
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✓</span>
                  <span><strong>Single Source of Truth:</strong> Ingest all customer channels into one unified intelligence repository.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✓</span>
                  <span><strong>Quantified Priorities:</strong> Every issue is backed by real frequency counts, severity, and customer sentiment scores.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✓</span>
                  <span><strong>One-Click Synthesis:</strong> AI clusters common themes and outlines strategic opportunities in seconds.</span>
                </li>
                <li className="flex items-start gap-2.5">
                  <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-700 flex items-center justify-center font-bold flex-shrink-0 text-[10px]">✓</span>
                  <span><strong>Engineered PRDs:</strong> Auto-generate user stories, Gherkin acceptance criteria, and technical constraints.</span>
                </li>
              </ul>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive ROI Calculator */}
      <section id="roi-calculator" className="py-16 md:py-24 bg-white border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
              Value Calculator
            </span>
            <h2 className="mt-3 text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight">
              Calculate your team's time & cost savings
            </h2>
            <p className="mt-3 text-base text-slate-600">
              Adjust your monthly feedback volume and team size to see immediate efficiency gains.
            </p>
          </div>

          <div className="bg-canvas max-w-4xl mx-auto p-6 sm:p-8 rounded-2xl border border-slate-200 shadow-sm grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
            {/* Controls */}
            <div className="space-y-6">
              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-2">
                  <span>Monthly Customer Feedback Items</span>
                  <span className="text-emerald-700 font-bold font-mono text-sm">{feedbackVolume} items</span>
                </div>
                <input
                  type="range"
                  min="50"
                  max="2000"
                  step="50"
                  value={feedbackVolume}
                  onChange={(e) => setFeedbackVolume(Number(e.target.value))}
                  className="w-full accent-emerald-600 cursor-pointer h-2 bg-slate-200 rounded-lg"
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                  <span>50 items</span>
                  <span>1,000 items</span>
                  <span>2,000+ items</span>
                </div>
              </div>

              <div>
                <div className="flex justify-between text-xs font-semibold text-slate-700 mb-2">
                  <span>Product & Engineering Team Size</span>
                  <span className="text-emerald-700 font-bold font-mono text-sm">{teamSize} members</span>
                </div>
                <input
                  type="range"
                  min="1"
                  max="50"
                  step="1"
                  value={teamSize}
                  onChange={(e) => setTeamSize(Number(e.target.value))}
                  className="w-full accent-emerald-600 cursor-pointer h-2 bg-slate-200 rounded-lg"
                />
                <div className="flex justify-between text-[10px] text-slate-400 mt-1">
                  <span>1 PM / Lead</span>
                  <span>25 members</span>
                  <span>50+ members</span>
                </div>
              </div>

              <div className="p-3.5 bg-white rounded-lg border border-slate-200 text-xs text-slate-600 flex items-center gap-2">
                <Sliders className="w-4 h-4 text-emerald-600 flex-shrink-0" />
                <span>Assumes industry standard 4.5 hrs/week per PM spent reading, tagging, and writing specs.</span>
              </div>
            </div>

            {/* Results Display */}
            <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-xs space-y-5 text-center sm:text-left">
              <div>
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Estimated Team Time Saved
                </span>
                <div className="text-3xl sm:text-4xl font-extrabold text-slate-900 mt-1">
                  ~{hoursSavedPerWeek} <span className="text-base font-semibold text-slate-500">hours / week</span>
                </div>
              </div>

              <div className="pt-4 border-t border-slate-100">
                <span className="text-xs font-semibold uppercase tracking-wider text-slate-500">
                  Projected Annual Cost Value
                </span>
                <div className="text-3xl sm:text-4xl font-extrabold text-emerald-600 mt-1">
                  ${estimatedAnnualSavings.toLocaleString()}
                  <span className="text-xs font-medium text-slate-500 ml-1">/ year</span>
                </div>
                <p className="text-[11px] text-slate-500 mt-1">
                  Reclaim valuable engineering time to ship features instead of triaging spreadsheets.
                </p>
              </div>

              <Link to="/register" className="block">
                <Button variant="primary" size="md" className="w-full" icon={ArrowRight}>
                  Start Saving Time Today
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16 md:py-24 bg-canvas border-b border-slate-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-14">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
              Customer Stories
            </span>
            <h2 className="mt-3 text-3xl sm:text-4xl font-extrabold text-slate-950 tracking-tight">
              Loved by product leads and founders
            </h2>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-6xl mx-auto">
            <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex text-amber-400 gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-amber-400" />
                  ))}
                </div>
                <p className="text-xs text-slate-700 leading-relaxed italic">
                  "Before FeedbackForge, our sprint planning meetings were endless debates between opinions. Now, every single initiative on our roadmap links back to 30+ categorized customer quotes and sentiment scores."
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-emerald-100 text-emerald-800 text-xs font-bold flex items-center justify-center">
                  SC
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900">Sarah Chen</h4>
                  <p className="text-[11px] text-slate-500">VP of Product, CloudFlow</p>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex text-amber-400 gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-amber-400" />
                  ))}
                </div>
                <p className="text-xs text-slate-700 leading-relaxed italic">
                  "The automated PRD generator is unbelievable. It translates customer complaints into clean acceptance criteria that my engineers can actually build against without endless clarification calls."
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-violet-100 text-violet-800 text-xs font-bold flex items-center justify-center">
                  DK
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900">David Kumar</h4>
                  <p className="text-[11px] text-slate-500">Head of Engineering, FinVibe</p>
                </div>
              </div>
            </div>

            <div className="p-6 rounded-xl bg-white border border-slate-200 shadow-xs flex flex-col justify-between">
              <div className="space-y-3">
                <div className="flex text-amber-400 gap-0.5">
                  {[...Array(5)].map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-amber-400" />
                  ))}
                </div>
                <p className="text-xs text-slate-700 leading-relaxed italic">
                  "We dropped our CSV of 800 Zendesk exports into FeedbackForge and within 40 seconds discovered a critical checkout bug costing us thousands in MRR that had slipped through the cracks."
                </p>
              </div>
              <div className="mt-6 pt-4 border-t border-slate-100 flex items-center gap-3">
                <div className="w-9 h-9 rounded-full bg-teal-100 text-teal-800 text-xs font-bold flex items-center justify-center">
                  EM
                </div>
                <div>
                  <h4 className="text-xs font-bold text-slate-900">Elena Rostova</h4>
                  <p className="text-[11px] text-slate-500">Founder & CEO, MetricsDock</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Frequently Asked Questions */}
      <section id="faq" className="py-16 md:py-24 bg-white border-b border-slate-200">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <span className="text-xs font-bold uppercase tracking-wider text-emerald-600 bg-emerald-50 px-3 py-1 rounded-full border border-emerald-200">
              Got Questions?
            </span>
            <h2 className="mt-3 text-3xl font-extrabold text-slate-950 tracking-tight">
              Frequently Asked Questions
            </h2>
          </div>

          <div className="space-y-3">
            {faqs.map((faq, idx) => {
              const isOpen = openFaqIndex === idx;
              return (
                <div
                  key={idx}
                  className="rounded-lg border border-slate-200 bg-white overflow-hidden transition-all shadow-xs"
                >
                  <button
                    type="button"
                    onClick={() => setOpenFaqIndex(isOpen ? -1 : idx)}
                    className="w-full px-5 py-4 text-left flex items-center justify-between gap-4 focus:outline-none"
                  >
                    <span className="text-sm font-bold text-slate-900">{faq.q}</span>
                    {isOpen ? (
                      <ChevronUp className="w-4 h-4 text-slate-500 flex-shrink-0" />
                    ) : (
                      <ChevronDown className="w-4 h-4 text-slate-400 flex-shrink-0" />
                    )}
                  </button>
                  {isOpen && (
                    <div className="px-5 pb-4 text-xs text-slate-600 leading-relaxed border-t border-slate-100 pt-3">
                      {faq.a}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* High-Converting Pre-Footer CTA */}
      <section className="py-16 md:py-20 bg-slate-950 text-white relative overflow-hidden">
        <div className="absolute inset-0 bg-[radial-gradient(#059669_1px,transparent_1px)] [background-size:24px_24px] opacity-20 pointer-events-none" />

        <div className="relative max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center space-y-6">
          <h2 className="text-2xl sm:text-4xl font-extrabold tracking-tight text-white">
            Ready to turn customer feedback into high-impact products?
          </h2>
          <p className="text-sm sm:text-base text-slate-400 max-w-xl mx-auto leading-relaxed">
            Join forward-thinking product managers, engineering teams, and founders. Set up your workspace in under two minutes.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-3 pt-2">
            <Link to="/register" className="w-full sm:w-auto">
              <Button
                variant="primary"
                size="lg"
                icon={ArrowRight}
                className="w-full sm:w-auto text-sm px-8 py-3 bg-emerald-500 hover:bg-emerald-400 text-slate-950 font-bold"
              >
                Create Free Workspace
              </Button>
            </Link>
            <Link to="/login" className="w-full sm:w-auto">
              <Button
                variant="outline"
                size="lg"
                className="w-full sm:w-auto text-sm px-7 py-3 text-slate-200 border-slate-700 hover:bg-slate-900"
              >
                Sign In to Account
              </Button>
            </Link>
          </div>
          <p className="text-[11px] text-slate-500">
            No credit card required • Unlimited free feedback ingestion for 14 days
          </p>
        </div>
      </section>

      {/* Comprehensive Footer */}
      <footer className="bg-white border-t border-slate-200 py-12 text-slate-600 text-xs">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 mb-8">
            {/* Brand Column */}
            <div className="col-span-2 md:col-span-1 space-y-3">
              <div className="flex items-center gap-2">
                <div className="w-7 h-7 rounded-md bg-emerald-600 flex items-center justify-center text-white">
                  <Compass className="w-4 h-4" />
                </div>
                <span className="text-sm font-bold text-slate-900">FeedbackForge AI</span>
              </div>
              <p className="text-slate-500 text-[11px] leading-relaxed">
                The Product Intelligence Workspace converting raw customer voice into validated engineering initiatives.
              </p>
            </div>

            {/* Product Links */}
            <div className="space-y-2">
              <h5 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">Product</h5>
              <ul className="space-y-1.5 text-slate-500">
                <li><a href="#features" className="hover:text-emerald-600">Feature Ingestion</a></li>
                <li><a href="#interactive-demo" className="hover:text-emerald-600">AI Clustering</a></li>
                <li><a href="#interactive-demo" className="hover:text-emerald-600">PRD Generator</a></li>
                <li><a href="#roi-calculator" className="hover:text-emerald-600">ROI Calculator</a></li>
              </ul>
            </div>

            {/* Resources Links */}
            <div className="space-y-2">
              <h5 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">Workspaces</h5>
              <ul className="space-y-1.5 text-slate-500">
                <li><Link to="/login" className="hover:text-emerald-600">Sign In</Link></li>
                <li><Link to="/register" className="hover:text-emerald-600">Create Account</Link></li>
                <li><Link to="/dashboard" className="hover:text-emerald-600">Product Dashboard</Link></li>
                <li><a href="#faq" className="hover:text-emerald-600">Documentation & FAQ</a></li>
              </ul>
            </div>

            {/* Trust & Compliance */}
            <div className="space-y-2">
              <h5 className="font-bold text-slate-900 uppercase tracking-wider text-[11px]">Security & Legal</h5>
              <ul className="space-y-1.5 text-slate-500">
                <li><span className="text-slate-500">SOC2 Type II Aligned</span></li>
                <li><span className="text-slate-500">End-to-End Encryption</span></li>
                <li><span className="text-slate-500">Privacy Policy</span></li>
                <li><span className="text-slate-500">Terms of Service</span></li>
              </ul>
            </div>
          </div>

          <div className="pt-8 border-t border-slate-200 flex flex-col sm:flex-row items-center justify-between gap-4 text-[11px] text-slate-400">
            <p>© {new Date().getFullYear()} FeedbackForge AI. Turn Customer Feedback into Product Decisions.</p>
            <div className="flex items-center gap-4">
              <span className="inline-flex items-center gap-1.5 text-emerald-700">
                <span className="w-2 h-2 rounded-full bg-emerald-500"></span> All systems operational
              </span>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}
