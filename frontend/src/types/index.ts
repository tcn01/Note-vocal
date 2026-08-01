// Auth & User
export interface User {
  id: number;
  email: string;
  name: string;
  preferred_language: string;
  role: string;
  grammar_level: string | null;
  is_active: boolean;
  created_at?: string;
}

export interface UserCreate {
  email: string;
  name: string;
  password: string;
  preferred_language?: string;
  role?: string;
}

export interface UserUpdate {
  email?: string;
  name?: string;
  password?: string;
  preferred_language?: string;
  role?: string;
  grammar_level?: string;
}

export interface UserGrammarLevelUpdate {
  grammar_level: string;
}

export interface UserGrammarSettings {
  id: number;
  user_id: number;
  start_level: string;
  current_order: number;
  daily_limit: number;
  last_study_date: string | null;
  lessons_today: number;
  updated_at?: string;
}

// Token
export interface Token {
  access_token: string;
  token_type?: string;
}

// Vocabulary
export interface Definition {
  partOfSpeech: string;
  meaning: string;
  example: string;
  memory_tip?: string;
  notes?: string;
}

export interface Vocabulary {
  id: number;
  user_id: number;
  word: string;
  ipa?: string;
  language: string;
  definitions: Definition[];
  pronunciation_url: string | null;
  examples: string[];
  synonyms: string[];
  memory_tip: string | null;
  notes: string | null;
  is_important: boolean;
  learned_date: string | null;
}

export interface VocabularyCreate {
  word: string;
  language: string;
  definitions?: Definition[];
  pronunciation_url?: string | null;
  examples?: string[];
  synonyms?: string[];
  memory_tip?: string | null;
  learned_date?: string | null;
  user_id: number;
}

export interface LookupWordRequest {
  word: string;
  language: string;
}

// Grammar
export interface GrammarTopic {
  id: number;
  order_num: number;
  topic: string;
  level: string;
  category: string;
  description: string;
  is_active: boolean;
}

export interface GrammarTopicProgress extends GrammarTopic {
  is_completed: boolean;
  is_reviewed: boolean;
  has_lesson: boolean;
  lesson_id: number | null;
  score: number | null;
}

export interface GrammarExample {
  sentence: string;
  translation: string;
}

export interface GrammarExercise {
  question: string;
  options: string[] | null;
  answer: string;
}

export interface GrammarLesson {
  id: number;
  user_id: number;
  topic_id: number | null;
  topic: string;
  level: string;
  explanation: string;
  examples: GrammarExample[];
  exercises: GrammarExercise[];
  generated_date: string;
  is_completed: boolean;
  is_reviewed: boolean;
  is_quiz_taken: boolean;
  score: number | null;
}

export interface GrammarLessonCreate {
  user_id: number;
  topic_id: number | null;
  topic: string;
  level: string;
  explanation: string;
  examples: GrammarExample[];
  exercises: GrammarExercise[];
  generated_date: string;
}

export interface GrammarLessonUpdate {
  is_completed?: boolean;
  is_reviewed?: boolean;
  is_quiz_taken?: boolean;
  score?: number;
}

export interface TodayPlan {
  review: GrammarLesson | null;
  new: GrammarTopic | null;
  message: string;
}

export interface GrammarGenerateRequest {
  topic_id: number;
}

// Test
export interface TestQuestion {
  id: number;
  type: 'multiple_choice' | 'fill_in_blank' | 'listening';
  question: string;
  options: string[] | null;
  word_audio: string | null;
  answer?: string;
}

export interface TestResult {
  id: number;
  user_id: number;
  test_type: string;
  start_date: string;
  end_date: string | null;
  questions: TestQuestion[];
  answers: Record<string, string> | null;
  total_questions: number;
  correct_answers: number;
  score: number | null;
}

export interface TestResultOut {
  id: number;
  test_type: string;
  start_date: string;
  end_date: string | null;
  total_questions: number;
  questions: TestQuestion[];
  score: number | null;
}

export interface TestResultDetail extends TestResult {
  results?: Record<string, {
    correct: boolean;
    user_answer: string;
    correct_answer: string;
  }>;
}

export interface TestGenerateRequest {
  start_date: string;
  end_date: string;
}

export interface TestSubmitRequest {
  answers: Record<string, string>;
}

// API Error
export interface ApiError {
  detail: string;
}