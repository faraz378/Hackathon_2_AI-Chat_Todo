/**
 * Chat page - AI-powered task management
 */
'use client';

import { useRouter } from 'next/navigation';
import ChatInterface from '@/components/chat/ChatInterface';
import { useRequireAuth } from '@/lib/auth/hooks';

export default function ChatPage() {
  const router = useRouter();
  const { user, isLoading } = useRequireAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-slate-900">
        <div className="text-slate-300">Loading...</div>
      </div>
    );
  }

  if (!user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-slate-900">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <h1 className="text-2xl font-bold text-slate-100">
              AI Task Assistant
            </h1>
            <button
              onClick={() => router.push('/dashboard')}
              className="text-slate-300 hover:text-slate-100 transition-colors"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      {/* Chat Interface */}
      <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <ChatInterface />
      </main>
    </div>
  );
}
