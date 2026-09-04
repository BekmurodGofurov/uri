/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        uzum: {
          DEFAULT: '#7000FF',
          50: '#f6f0ff',
          100: '#ede2fe',
          200: '#dbc8fd',
          300: '#bfa0fb',
          400: '#9d6ef7',
          500: '#7000ff',
          600: '#6400e6',
          700: '#5300bf',
          800: '#430299',
          900: '#38067b',
          950: '#1b0042',
        },
      },
    },
  },
  plugins: [],
}
