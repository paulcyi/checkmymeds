/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{ts,tsx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'ui-sans-serif', 'system-ui'],
      },
      colors: {
        'cmm-surface': {
          DEFAULT: '#ffffff',
          900: '#0d1117',
        },
        'cmm-primary': {
          50: '#e6f7f6',
          100: '#b3ece8',
          200: '#80e1da',
          300: '#4dd6cc',
          400: '#1acbbc',
          500: '#0d9488',
          600: '#0b786f',
          700: '#095c55',
          800: '#06413c',
          900: '#022621',
        },
        'cmm-accent': {
          50: '#eef6ff',
          100: '#cfe6ff',
          200: '#afd5ff',
          300: '#8fc4ff',
          400: '#70b3ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#153bb5',
          900: '#0d2883',
        },
        'cmm-severity': {
          mild: '#facc15',
          mod: '#f97316',
          severe: '#ef4444',
        },
      },
    },
  },
  plugins: [],
};
