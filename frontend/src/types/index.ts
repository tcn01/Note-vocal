export interface User {
  id: number
  email: string
  name: string
  preferred_language: string
  is_active: boolean
  created_at?: string
}

export interface UserCreate {
  email: string
  name: string
  password: string
  preferred_language?: string
}

export interface LoginRequest {
  email: string
  password: string
}

export interface Token {
  access_token: string
  token_type: string
}

export interface Vocabulary {
  id: number
  user_id: number
  word: string
  language: string
  definitions: string[]
  pronunciation_url?: string
  examples: string[]
  synonyms: string[]
  memory_tip?: string
  learned_date?: string
}

export interface GrammarLesson {
  id: number
  user_id: number
  topic: string
  level: string
  explanation: string
  examples: string[]
  exercises: Record<string, unknown>[]
  generated_date: string
  is_completed: boolean
  is_quiz_taken: boolean
  score?: number
}

export interface TestResult {
  id: number
  user_id: number
  test_type: string
  start_date: string
  end_date?: string
  total_questions: number
  correct_answers: number
  score?: number
}
