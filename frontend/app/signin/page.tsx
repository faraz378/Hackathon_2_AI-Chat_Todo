/**
 * Signin page - Premium Dark Theme
 * Elegant authentication with modern design
 */

import Link from 'next/link';
import SigninForm from '@/components/auth/SigninForm';

export default function SigninPage() {
  return (
    <div className="min-h-screen flex items-center justify-center px-4 py-12 relative overflow-hidden">
      {/* Background Effects */}
      <div className="absolute inset-0 bg-linear-to-br from-indigo-900/70 via-transparent to-purple-900/60 pointer-events-none"></div>
      <div className="absolute top-1/3 right-1/4 w-96 h-96 bg-indigo-600/10 rounded-full blur-3xl pointer-events-none"></div>

      <div className="w-full max-w-md relative z-10 animate-fade-in">
        {/* Header */}
        <div className="text-center mb-8">
          <Link href="/" className="inline-block mb-6 group">
            <div className="flex items-center gap-2 text-slate-300 hover:text-indigo-500 transition-colors">
              <svg className="w-6 h-6 group-hover:-translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 19l-7-7m0 0l7-7m-7 7h18" />
              </svg>
              <span className="font-medium">Back to Home</span>
            </div>
          </Link>

          <h2 className="text-4xl font-bold text-slate-400 mb-3">
            Welcome Back
          </h2>
          <p className="text-slate-300 text-lg">
            Sign in to continue to your tasks
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-slate-800/30 backdrop-blur-sm border border-slate-700/50 rounded-2xl p-8 shadow-xl">
          <SigninForm />
        </div>

        {/* Footer */}
        <div className="mt-6 text-center">
          <p className="text-slate-200">
            Don't have an account?{' '}
            <Link
              href="/signup"
              className="text-indigo-300 hover:text-indigo-500 font-semibold transition-colors"
            >
              Sign up
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
