// AdminLayout.jsx - Beautiful Admin Layout with Sidebar & Header
import React, { useState } from 'react'
import { useLocation } from 'react-router-dom'
import { Menu, X, LogOut, Settings } from 'lucide-react'
import Navbar from '../layout/Navbar'

export function AdminLayout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const location = useLocation()

  const menuItems = [
    { label: 'Dashboard', icon: '📊', href: '/admin' },
    { label: 'Courses', icon: '📚', href: '/admin/courses' },
    { label: 'Analytics', icon: '📈', href: '/admin/analytics' },
    { label: 'Settings', icon: '⚙️', href: '/admin/settings' }
  ]

  return (
    <div className="flex h-screen bg-gray-900">
      {/* SIDEBAR */}
      <div
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gray-950 border-r border-gray-800 transition-all duration-300 flex flex-col`}
      >
        {/* LOGO */}
        <div className="p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold">SK</span>
            </div>
            {sidebarOpen && (
              <div>
                <h1 className="text-white font-bold">LearnTrack</h1>
                <p className="text-gray-500 text-xs">Admin</p>
              </div>
            )}
          </div>
        </div>

        {/* MENU */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item) => (
            <a
              key={item.href}
              href={item.href}
              className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                location.pathname === item.href
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-400 hover:bg-gray-800'
              }`}
            >
              <span className="text-lg">{item.icon}</span>
              {sidebarOpen && <span>{item.label}</span>}
            </a>
          ))}
        </nav>

        {/* TOGGLE */}
        <div className="p-4 border-t border-gray-800">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="w-full flex items-center justify-center p-2 text-gray-400 hover:text-white rounded-lg hover:bg-gray-800"
          >
            {sidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </div>

      {/* MAIN CONTENT */}
      <div className="flex-1 flex flex-col overflow-hidden">
        <Navbar />
        <main className="flex-1 overflow-auto bg-gray-900">
          {children}
        </main>
      </div>
    </div>
  )
}
