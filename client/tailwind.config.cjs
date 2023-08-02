const config = {
  content: ['./src/**/*.{html,js,svelte,ts}'],

  theme: {
    screens: {
      sm: '0rem',
      md: '48rem',
      lg: '72rem',
    },
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
