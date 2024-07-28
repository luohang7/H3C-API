const path = require('path');
const { VuetifyLoaderPlugin } = require('vuetify-loader');

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
      },
      '/stop_script':{
        target: 'http://localhost:5000',
        changeOrigin: true
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        ws: true,
        changeOrigin: true
      }
    }
  },

  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    },
    plugins: [
      new VuetifyLoaderPlugin()
    ]
  },

  css: {
    loaderOptions: {
      css: {
        importLoaders: 1
      },
      postcss: {
        postcssOptions: {
          plugins: [
            require('autoprefixer')
          ]
        }
      }
    }
  },

  transpileDependencies: [
    'vuetify'
  ]
};
