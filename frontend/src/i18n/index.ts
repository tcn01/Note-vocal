import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';

const resources = {
  en: {
    translation: {
      // Navigation
      'nav.vocabulary': 'Vocabulary',
      'nav.grammar': 'Grammar',
      'nav.tests': 'Tests',
      'nav.profile': 'Profile',
      'nav.logout': 'Logout',
      
      // Login
      'login.title': 'Login',
      'login.email': 'Email',
      'login.password': 'Password',
      'login.button': 'Login',
      'login.noAccount': "Don't have an account?",
      'login.register': 'Register',
      'login.error': 'Incorrect email or password',
      
      // Register
      'register.title': 'Register',
      'register.name': 'Name',
      'register.button': 'Register',
      'register.hasAccount': 'Already have an account?',
      'register.login': 'Login',
      
      // Vocabulary
      'vocab.title': 'Vocabulary',
      'vocab.addWord': 'Add Word',
      'vocab.word': 'Word',
      'vocab.language': 'Language',
      'vocab.lookup': 'Look Up',
      'vocab.loading': 'Looking up...',
      'vocab.existing': 'This word already exists',
      'vocab.myWords': 'My Vocabulary',
      'vocab.filter': 'Filter by Date',
      'vocab.from': 'From',
      'vocab.to': 'To',
      'vocab.apply': 'Apply',
      'vocab.audio': 'Audio',
      'vocab.definitions': 'Definitions',
      'vocab.examples': 'Examples',
      'vocab.synonyms': 'Synonyms',
      'vocab.memoryTip': 'Memory Tip',
      
      // Grammar
      'grammar.title': 'Grammar',
      'grammar.today': "Today's Plan",
      'grammar.review': 'Review',
      'grammar.new': 'New Lesson',
      'grammar.learnNow': 'Learn Now',
      'grammar.reviewDone': 'Review Done',
      'grammar.complete': 'Complete',
      'grammar.limitReached': "Daily limit reached",
      'grammar.learnMore': 'Learn More',
      'grammar.curriculum': 'Curriculum',
      'grammar.setLevel': 'Set Your Level',
      'grammar.levelA1': 'Beginner (A1)',
      'grammar.levelA2': 'Elementary (A2)',
      'grammar.levelB1': 'Intermediate (B1)',
      'grammar.levelB2': 'Upper Intermediate (B2)',
      
      // Tests
      'tests.title': 'Tests',
      'tests.generate': 'Generate Test',
      'tests.selectDate': 'Select Date Range',
      'tests.from': 'From',
      'tests.to': 'To',
      'tests.create': 'Create Test',
      'tests.loading': 'Generating...',
      'tests.notEnoughWords': 'Not enough words. Add more vocabulary first.',
      'tests.submit': 'Submit',
      'tests.score': 'Score',
      'tests.correct': 'Correct',
      'tests.wrong': 'Wrong',
      'tests.history': 'Test History',
      
      // Profile
      'profile.title': 'Profile',
      'profile.name': 'Name',
      'profile.email': 'Email',
      'profile.grammarLevel': 'Grammar Level',
      'profile.language': 'Language Preference',
      'profile.save': 'Save',
    },
  },
  vi: {
    translation: {
      // Navigation
      'nav.vocabulary': 'Từ Vựng',
      'nav.grammar': 'Ngữ Pháp',
      'nav.tests': 'Bài Kiểm Tra',
      'nav.profile': 'Hồ Sơ',
      'nav.logout': 'Đăng Xuất',
      
      // Login
      'login.title': 'Đăng Nhập',
      'login.email': 'Email',
      'login.password': 'Mật Khẩu',
      'login.button': 'Đăng Nhập',
      'login.noAccount': 'Chưa có tài khoản?',
      'login.register': 'Đăng Ký',
      'login.error': 'Email hoặc mật khẩu không đúng',
      
      // Register
      'register.title': 'Đăng Ký',
      'register.name': 'Tên',
      'register.button': 'Đăng Ký',
      'register.hasAccount': 'Đã có tài khoản?',
      'register.login': 'Đăng Nhập',
      
      // Vocabulary
      'vocab.title': 'Từ Vựng',
      'vocab.addWord': 'Thêm Từ',
      'vocab.word': 'Từ',
      'vocab.language': 'Ngôn Ngữ',
      'vocab.lookup': 'Tra Cứu',
      'vocab.loading': 'Đang tra cứu...',
      'vocab.existing': 'Từ này đã tồn tại',
      'vocab.myWords': 'Từ Vựng Của Tôi',
      'vocab.filter': 'Lọc Theo Ngày',
      'vocab.from': 'Từ',
      'vocab.to': 'Đến',
      'vocab.apply': 'Áp Dụng',
      'vocab.audio': 'Phát Âm',
      'vocab.definitions': 'Định Nghĩa',
      'vocab.examples': 'Ví Dụ',
      'vocab.synonyms': 'Đồng Nghĩa',
      'vocab.memoryTip': 'Mẹo Nhớ',
      
      // Grammar
      'grammar.title': 'Ngữ Pháp',
      'grammar.today': 'Kế Hoạch Hôm Nay',
      'grammar.review': 'Ôn Tập',
      'grammar.new': 'Bài Mới',
      'grammar.learnNow': 'Học Ngay',
      'grammar.reviewDone': 'Đã Ôn Xong',
      'grammar.complete': 'Hoàn Thành',
      'grammar.limitReached': 'Đã hết giới hạn hàng ngày',
      'grammar.learnMore': 'Học Thêm',
      'grammar.curriculum': 'Chương Trình',
      'grammar.setLevel': 'Chọn Trình Độ',
      'grammar.levelA1': 'Mới Bắt Đầu (A1)',
      'grammar.levelA2': 'Sơ Cấp (A2)',
      'grammar.levelB1': 'Trung Cấp (B1)',
      'grammar.levelB2': 'Trung Cấp Cao (B2)',
      
      // Tests
      'tests.title': 'Bài Kiểm Tra',
      'tests.generate': 'Tạo Đề',
      'tests.selectDate': 'Chọn Khoảng Ngày',
      'tests.from': 'Từ',
      'tests.to': 'Đến',
      'tests.create': 'Tạo Đề',
      'tests.loading': 'Đang tạo...',
      'tests.notEnoughWords': 'Không đủ từ. Hãy thêm từ vựng trước.',
      'tests.submit': 'Nộp Bài',
      'tests.score': 'Điểm',
      'tests.correct': 'Đúng',
      'tests.wrong': 'Sai',
      'tests.history': 'Lịch Sử Bài Kiểm Tra',
      
      // Profile
      'profile.title': 'Hồ Sơ',
      'profile.name': 'Tên',
      'profile.email': 'Email',
      'profile.grammarLevel': 'Trình Độ Ngữ Pháp',
      'profile.language': 'Ngôn Ngữ Giao Diện',
      'profile.save': 'Lưu',
    },
  },
};

i18n
  .use(initReactI18next)
  .init({
    resources,
    lng: 'vi',
    fallbackLng: 'en',
    interpolation: {
      escapeValue: false,
    },
  });

export default i18n;