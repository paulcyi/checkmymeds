// postcss.config.js
module.exports = {
  plugins: {
    // Tailwind v3 needs explicit nesting plugin
    'tailwindcss/nesting': {},
    tailwindcss: {},
    autoprefixer: {},
  },
};
