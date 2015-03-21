module.exports = function(grunt) {

  // Project configuration.
  grunt.initConfig({
    pkg: grunt.file.readJSON('package.json'),
    uglify: {
      options: {
        banner: '/*! <%= pkg.name %> <%= grunt.template.today("yyyy-mm-dd") %> */\n'
      },
      build: {
        src: 'src/<%= pkg.name %>.js',
        dest: 'build/<%= pkg.name %>.min.js'
      }
    },
    dojo: {
      dist: {
        options: {
          dojo: 'node_modules/dojo/dojo.js', // Path to dojo.js file in dojo source 
          load: 'build', // Optional: Utility to bootstrap (Default: 'build') 
          profile: 'app.profile.js', // Profile for build 
          profiles: [], // Optional: Array of Profiles for build 
          appConfigFile: '', // Optional: Config file for dojox/app 
          package: '', // Optional: Location to search package.json (Default: nothing) 
          packages: [], // Optional: Array of locations of package.json (Default: nothing) 
          require: '', // Optional: Module to require for the build (Default: nothing) 
          requires: [], // Optional: Array of modules to require for the build (Default: nothing) 
          action: '', // Optional: Build action, release, help. clean has been deprecated. 
          cwd: './', // Directory to execute build within 
          dojoConfig: '', // Optional: Location of dojoConfig (Default: null), 
          // Optional: Base Path to pass at the command line 
          // Takes precedence over other basePaths 
          // Default: null 
          basePath: ''
        }
      },
      options: {
        // You can also specify options to be used in all your tasks 
        dojo: 'node_modules/dojo/dojo.js', // Path to dojo.js file in dojo source 
        load: 'build', // Optional: Utility to bootstrap (Default: 'build') 
        profile: 'app.profile.js', // Profile for build 
        profiles: [], // Optional: Array of Profiles for build 
        appConfigFile: '', // Optional: Config file for dojox/app 
        package: '', // Optional: Location to search package.json (Default: nothing) 
        packages: [], // Optional: Array of locations of package.json (Default: nothing) 
        require: '', // Optional: Module to require for the build (Default: nothing) 
        requires: [], // Optional: Array of modules to require for the build (Default: nothing) 
        action: '', // Optional: Build action, release, help. clean has been deprecated. 
        cwd: './', // Directory to execute build within 
        dojoConfig: '', // Optional: Location of dojoConfig (Default: null), 
        // Optional: Base Path to pass at the command line 
        // Takes precedence over other basePaths 
        // Default: null 
        basePath: ''
      }
    }
  });
  
  // Load the plugin that provides dojo build
  grunt.loadNpmTasks('grunt-dojo');

  // Load the plugin that provides the "uglify" task.
  grunt.loadNpmTasks('grunt-contrib-uglify');

  // Default task(s).
  grunt.registerTask('default', ['uglify']);

};
