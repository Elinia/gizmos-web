const config = {
  content: ['./src/**/*.{html,js,svelte,ts}'],

  theme: {
    extend: {
      fontSize: {
        '2xs': [
          '0.5625rem',
          {
            lineHeight: '0.75rem',
          },
        ],
      },
    },
  },

  plugins: [],
}

module.exports = config
