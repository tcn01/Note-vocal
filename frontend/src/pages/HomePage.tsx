import { useTranslation } from "react-i18next"

export function HomePage() {
  const { t } = useTranslation()

  return (
    <div className="text-center">
      <h1 className="mt-20 text-4xl font-bold text-gray-800">VisionNest</h1>
      <p className="mt-4 text-lg text-gray-600">
        Học ngôn ngữ thông minh với AI
      </p>
    </div>
  )
}
