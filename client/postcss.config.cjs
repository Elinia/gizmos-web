const autoprefixer = require('autoprefixer')
const nesting = require('postcss-nesting')
const unocss = require('@unocss/postcss')

const config = {
  plugins: [unocss, nesting(), autoprefixer],
}

module.exports = config
