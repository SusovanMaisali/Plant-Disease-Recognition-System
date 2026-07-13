/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        cs: {
          bg: '#040d06',
          card: '#08170c',
          cardlight: '#0c2414',
          border: '#12331d',
          mint: '#10b981',
          emerald: '#059669',
          muted: '#84a38e',
          text: '#e2f0e6',
        }
      }
    },
  },
  plugins: [],
}
