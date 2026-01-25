'use client';

/**
 * Landing page - Premium Dark Theme
 * Modern, elegant hero section with smooth animations
 */

import Link from 'next/link';

export default function HomePage() {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Gradient Background Effect */}
      <div className="absolute inset-0 bg-linear-to-br from-indigo-900/20 via-transparent to-purple-900/10 pointer-events-none"></div>
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="max-w-4xl mx-auto text-center relative z-10 animate-fade-in">
        {/* Logo/Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-indigo-500/10 border border-indigo-500/20 mb-8 animate-scale-in">
          <div className="w-2 h-2 bg-indigo-100 rounded-full animate-pulse"></div>
          <span className="text-sm font-medium text-indigo-300">Modern Task Management</span>
        </div>

        {/* Hero Heading */}
        <h1 className="text-6xl md:text-7xl font-bold mb-6 bg-linear-to-r from-slate-100 via-indigo-500 to-slate-100 bg-clip-text text-transparent leading-tight">
          Organize Your Life
          <br />
          <span className="text-indigo-400">Effortlessly</span>
        </h1>

        {/* Subheading */}
        <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-2xl mx-auto leading-relaxed">
          A beautiful, secure, and intuitive task management app designed for modern productivity
        </p>

        {/* CTA Buttons */}
        <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
          <Link
            href="/signup"
            className="group px-8 py-4 bg-indigo-600 text-white rounded-xl font-semibold text-lg hover:bg-indigo-500 transition-all duration-200 shadow-lg hover:shadow-indigo-500/50 hover:scale-105 active:scale-100"
          >
            <span className="flex items-center gap-2">
              Get Started Free
              <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </span>
          </Link>
          <Link
            href="/signin"
            className="px-8 py-4 bg-slate-800 text-slate-100 border border-slate-700 rounded-xl font-semibold text-lg hover:bg-slate-700 hover:border-slate-600 transition-all duration-200 hover:scale-105 active:scale-100"
          >
            Sign In
          </Link>
        </div>

        {/* Feature Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-20">
          {/* Feature 1 */}
          <div className="group p-8 rounded-2xl bg-slate-800/50 border border-slate-700/50 backdrop-blur-sm hover:bg-slate-800/70 hover:border-indigo-500/50 transition-all duration-300 hover:scale-105 animate-slide-in">
            <div className="w-14 h-14 rounded-xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mb-6 group-hover:bg-indigo-500/20 transition-colors">
              <svg className="w-7 h-7 text-indigo-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-100 mb-3">Simple & Intuitive</h3>
            <p className="text-slate-400 leading-relaxed">
              Clean interface designed for focus. Manage tasks without the complexity.
            </p>
          </div>

          {/* Feature 2 */}
          <div className="group p-8 rounded-2xl bg-slate-800/50 border border-slate-700/50 backdrop-blur-sm hover:bg-slate-800/70 hover:border-indigo-500/50 transition-all duration-300 hover:scale-105 animate-slide-in" style={{ animationDelay: '100ms' }}>
            <div className="w-14 h-14 rounded-xl bg-emerald-500/10 border border-emerald-500/20 flex items-center justify-center mb-6 group-hover:bg-emerald-500/20 transition-colors">
              <svg className="w-7 h-7 text-emerald-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-100 mb-3">Secure & Private</h3>
            <p className="text-slate-400 leading-relaxed">
              Your data is encrypted and protected with industry-standard security.
            </p>
          </div>

          {/* Feature 3 */}
          <div className="group p-8 rounded-2xl bg-slate-800/50 border border-slate-700/50 backdrop-blur-sm hover:bg-slate-800/70 hover:border-indigo-500/50 transition-all duration-300 hover:scale-105 animate-slide-in" style={{ animationDelay: '200ms' }}>
            <div className="w-14 h-14 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center mb-6 group-hover:bg-purple-500/20 transition-colors">
              <svg className="w-7 h-7 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
            </div>
            <h3 className="text-xl font-semibold text-slate-100 mb-3">Works Everywhere</h3>
            <p className="text-slate-400 leading-relaxed">
              Seamlessly responsive across desktop, tablet, and mobile devices.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
