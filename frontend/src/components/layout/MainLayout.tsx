import { Link } from "react-router-dom"
import { useTranslation } from "react-i18next"
import type { ReactNode } from "react"
import { useAuth } from "../../hooks/useAuth"

interface Props {
  children: ReactNode
}

export function MainLayout({ children }: Props) {
  const { t, i18n } = useTranslation()
  const { isAuthenticated, logout } = useAuth()

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <Link to="/" className="text-xl font-bold text-blue-600">
            VisionNest
          </Link>
          <nav className="flex items-center gap-4">
            <Link to="/vocabulary" className="text-gray-600 hover:text-blue-600">{t("nav.vocabulary")}</Link>
            <Link to="/grammar" className="text-gray-600 hover:text-blue-600">{t("nav.grammar")}</Link>
            <Link to="/test" className="text-gray-600 hover:text-blue-600">{t("nav.test")}</Link>
            <select
              value={i18n.language}
              onChange={(e) => i18n.changeLanguage(e.target.value)}
              className="rounded border px-2 py-1 text-sm"
            >
              <option value="vi">Tiếng Việt</option>
              <option value="en">English</option>
              <option value="zh">中文</option>
            </select>
            {isAuthenticated ? (
              <button onClick={logout} className="text-red-500 hover:text-red-700">
                {t("nav.logout")}
              </button>
            ) : (
              <Link to="/login" className="text-blue-600 hover:text-blue-800">{t("nav.login")}</Link>
            )}
          </nav>
        </div>
      </header>
      <main className="mx-auto max-w-6xl px-4 py-6">{children}</main>
    </div>
  )
}
