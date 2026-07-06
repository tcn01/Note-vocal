import { AppRouter } from "./routes"
import { MainLayout } from "./components/layout/MainLayout"

function App() {
  return (
    <MainLayout>
      <AppRouter />
    </MainLayout>
  )
}

export default App
