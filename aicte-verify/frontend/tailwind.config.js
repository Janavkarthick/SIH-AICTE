/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        aicte: {
          50: '#eef6ff',
          100: '#d9eaff',
          200: '#bcd9ff',
          300: '#8ec0ff',
          400: '#599eff',
          500: '#327bf7',
          600: '#1b5ceb',
          700: '#1547d8',
          800: '#173aad',
          900: '#183488',
          950: '#122053',
        },
      },
    },
  },
  plugins: [],
}
