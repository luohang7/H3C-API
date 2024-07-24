const path = require('path');

module.exports = {
  devServer: {
    proxy: {
      '/run_script': {
        target: 'http://localhost:5000',
        changeOrigin: true
      },
       '/upload_csv': {
        target: 'http://localhost:5000',
        changeOrigin: true
      }
    }
  },
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  },
    css: {
    loaderOptions: {
      sass: {
        additionalData: `@import "~vuetify/src/styles/styles.sass"`
      }
    }
  }
};
