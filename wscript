# How to use
# ==========
#   ./waf configure --download --engine=[dojo] --platform=[android|local|chrome|owa]
#   ./waf build --partial --bT=[debug|release]
#   ./waf install
#   ./waf dist_[chrome]


import sys;
import os;
import stat;
import shutil;
import urllib;
import zipfile;
import shlex,subprocess;
import multiprocessing;
import json;
from string import Template;
import platform;
import time;

APPNAME = 'webRoot' #set Your Project Name Here
VERSION = '1' #set Your Project Version Here (only used internally by waf on build)

ANDROID_PACKAGE = "com.fairydwarves.webboilerplate" #set your android package identifier when applicable
ANDROID_PROJECT = "webBoilerPlate" #set your android app name when applicable

DIJIT = 1 #do we use dijit ?
DIJIT_THEMES = ['nihilo'] #set the list of dijit themes we want to build

BUILDTYPES = 'debug release'
ENV_FN = 'Environment.js' #platform env file
WINDOWS_SLEEP_DURATION = 0.1 #used on MS windows platforms to allow folder deletion to occur

top = '.'
out = 'wbuild'
jsOut = '_release' #JS build folder name
jsBuildFiles = ['app/app.js', 'dojo/dojo.js'] #results of JS build: add other built files you want to copy here


def options(opt):
    """ Defines which option can be used for this project """
    opt.recurse('depends')
    opt.recurse('tools')
    
    opt.add_option('--partial', action='store_true', default=False, help='do not rebuild the app if build folder is present [True | False (default)')

    opt.add_option('--bT', action='store', default='release', help='build type [debug | release (default)]')

def configure(conf):
    conf.check_waf_version(mini='1.6.3')

    #running configure in depends
    depends_dir= conf.path.find_dir('depends')
    if depends_dir is not None : conf.recurse('depends')

    # Finding the htdocs folder, the root
    htdocsnode = conf.path.find_dir('htdocs')
    if htdocsnode is None : conf.fatal("htdocs/ subfolder was not found. Cannot continue.")
    
    # Finding the scripts folder where to put build results
    scriptsnode = htdocsnode.find_dir('scripts')
    if scriptsnode is None : conf.fatal("htdocs/scripts/ subfolder was not found. Cannot continue.")


    #copying depends single files and folders cpntent
    for depend in conf.env.DEPENDS:
        dependNode = depends_dir.find_node(depend)
        if dependNode is None: conf.fatal(depend + " was not found. Please run waf configure --download.")
        #else: print depend + " path " + dependNode.abspath()

        if os.path.isdir(dependNode.abspath()) : #FOLDER HANDLING
            conf.start_msg("Retrieving " + depend )
            files = os.listdir(dependNode.abspath())
            for file in files:
                src_file = os.path.join(dependNode.abspath(), file)
                dst_file = os.path.join(scriptsnode.abspath(), file)
                if os.path.exists(dst_file) : #remove existing dir
                    shutil.rmtree(dst_file)
                    if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION)
                shutil.move(src_file, dst_file)
            conf.end_msg(scriptsnode.relpath() + " : [" + ', '.join(files)+ "]")
        else : #FILE HANDLING
            conf.start_msg("Retrieving " + depend )
            shutil.copy(dependNode.abspath(),scriptsnode.abspath())
            conf.end_msg( scriptsnode.find_node(os.path.basename(dependNode.abspath())).relpath())

    #handling ENGINE
    if conf.env.ENGINE == "dojo":
        if DIJIT :
            #extracting dijit themes
            dijitthemes = scriptsnode.find_node("dijit/themes")
            if dijitthemes is None : conf.fatal("dijit/themes for dijit themes was not found in build directory. Cannot continue.")
            conf.start_msg( "Extracting Dijit Themes ")
            cssNode = htdocsnode.find_node("css")
            #copying dijit.css
            shutil.copy(dijitthemes.find_node("dijit.css").get_src().abspath(), cssNode.abspath() )
            #copying dijit themes (not built)
            for tname in DIJIT_THEMES :
                thdir = dijitthemes.find_dir(tname)
                if thdir is not None :
                    cssThDir = cssNode.make_node(tname)
                    if os.path.exists(cssThDir.abspath()) :
                        shutil.rmtree(cssThDir.abspath())
                        if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION*4)
                    shutil.copytree (thdir.abspath(), cssThDir.abspath() )
            conf.end_msg( cssNode.relpath() )
            
            #copying dijit/icons into htdocs/icons
            dijiticons = scriptsnode.find_node("dijit/icons")
            if dijiticons is None : conf.fatal("dijit/icons for dijit icons was not found in build directory. Cannot continue.")
            conf.start_msg( "Extracting Dijit Icons ")
            htdocsIconsNode = htdocsnode.make_node("icons") 
            if os.path.exists(htdocsIconsNode.abspath()) :
                shutil.rmtree(htdocsIconsNode.abspath())
                if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION*60)
            shutil.copytree (dijiticons.abspath(), htdocsIconsNode.abspath() )
            conf.end_msg( htdocsIconsNode.relpath() )

        # Copying doh for testing purposes into our tests directory
        testsnode =  scriptsnode.find_dir('app').find_dir('tests')
        if testsnode is not None :
            dohnode = scriptsnode.find_dir('util/doh')
            if dohnode is None : conf.fatal("util/doh subfolder was not found in dojo directory. Cannot continue.")
  
            dohdstnode = testsnode.make_node('doh')
            conf.start_msg( "Copying " + dohnode.relpath() + " to " + dohdstnode.relpath() )
            if os.path.exists(dohdstnode.relpath()) :
                shutil.rmtree(dohdstnode.relpath())
                if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION*10)
            shutil.copytree(dohnode.relpath(), dohdstnode.relpath())
            conf.end_msg( "ok" )
        #else: conf.fatal("tests/ subfolder was not found. Cannot continue.")

        if conf.env.PLATFORM == 'android':

            #TODO CHECK IF WE STILL NEED MANUAL MOBILE THEME COPY
            print ">>> TODO CHECK IF WE STILL NEED MANUAL MOBILE THEME COPY <<<"

#            #extracting dojox mobile themes
#            conf.start_msg("Extracting Dojox mobile Theme chooser" )
#            # creating dojox folder
#            htdocsdojoxnode = htdocsnode.make_node(os.path.dirname(dojoxmobilethemechooser.path_from(scriptsnode)))
#            if not os.path.exists(htdocsdojoxnode.abspath()) :
#                htdocsdojoxnode.mkdir()
#            shutil.copy(dojoxmobilethemechooser.abspath(),htdocsnode.make_node(dojoxmobilethemechooser.path_from(scriptsnode)).abspath())
#            conf.end_msg( htdocsnode.find_node(dojoxmobilethemechooser.path_from(scriptsnode)).relpath())
        
            conf.start_msg( "Extracting Dojox Mobile Themes ")
            dmblthemes_build = scriptsnode.find_node("dojox/mobile/themes")
            if dmblthemes_build is None : conf.fatal("dojox/mobile/themes for dojox mobile themes was not found in build directory. Cannot continue.")
            htdocsDojoxNode = htdocsnode.make_node("dojox");
            dmbltnode = htdocsnode.make_node("dojox/mobile/themes")
            if os.path.exists(htdocsDojoxNode.abspath()) : #remove existing dojox dir
                shutil.rmtree(htdocsDojoxNode.abspath(), 1)
                if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION*5)
            dmbltnode.mkdir()
            for ftname in ['android','blackberry','common','custom','holodark','iphone','windows']:
                thdir = dmblthemes_build.find_dir(ftname)
                if thdir is not None :
                    thcss = thdir.find_node(ftname + ".css")
                    if thcss is not None :
                        thnode = dmbltnode.make_node(ftname)
                        thnode.mkdir()
                        if thnode is not None :
                            #copy the css
                            shutil.copy( thcss.abspath(), thnode.abspath())
                
                            #copy the images
                            thimg = thdir.find_dir("images")
                            if thimg is not None :
                                thimagesnode = thnode.make_node("images")
                                if os.path.exists(thimagesnode.abspath()) : #remove existing images dir
                                    shutil.rmtree(thimagesnode.abspath())
                                    if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION)
                                shutil.copytree (thimg.abspath(), thimagesnode.abspath() )
                  
                            #ipad specific from iphone theme
                            ipadcss = thdir.find_node("ipad.css")
                            if ipadcss is not None :
                                shutil.copy( ipadcss.abspath(), thnode.abspath())
          
            conf.end_msg( "ok" )

    else: # no need of dojo
        pass
    #end of conf.env.ENGINE

    #handling PLATFORM
    if conf.env.PLATFORM == 'android' :
        #preparing cordova project
        conf.start_msg("Checking Cordova Project")
        cordova_create_node = conf.path.find_node(conf.env.CORDOVA_PATH).find_node("bin").find_node("create")
        if cordova_create_node is None : conf.fatal("bin/create was not found in " + conf.env.CORDOVA_PATH + ". Cannot continue.")


        #nodeJS detection
        def detect_nodeJS() :
            conf.start_msg("=> NodeJS bin/ should be in your PATH")
            ant_detect = subprocess.Popen(
                "node -v",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True,
            )
            out,err = ant_detect.communicate()
            if ant_detect.returncode == 0 :
                conf.to_log(out)
                conf.to_log(err)
                conf.end_msg("ok","GREEN")
                return True;
            else :
                conf.end_msg("failed","RED")
                conf.fatal("Command Output : \n" + out + "Error :\n" + err)
        
        android_pub_node = conf.path.find_node("publish").find_node("android")
        if android_pub_node is None : conf.fatal("Cannot find publish/android path")
        android_proj_node = android_pub_node.find_node(ANDROID_PROJECT);
        if android_proj_node is None :
            conf.end_msg("failed","RED")
            #detecting nodeJS http://cordova.apache.org/docs/en/3.4.0/guide_cli_index.md.html#The%20Command-Line%20Interface
            if detect_nodeJS():
                conf.start_msg("Building Cordova Project")
                cordova_create_proc = subprocess.Popen(
                    cordova_create_node.abspath() + " " + os.path.join(android_pub_node.path_from(conf.path),ANDROID_PROJECT) + " " + ANDROID_PACKAGE + " " + ANDROID_PROJECT,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    shell=True
                )
                out,err = cordova_create_proc.communicate()
                if cordova_create_proc.returncode == 0 :
                    conf.to_log(out)
                    conf.to_log(err)
                    android_proj_node = android_pub_node.find_node(ANDROID_PROJECT);
                    if android_proj_node is None : conf.fatal(ANDROID_PROJECT + " was not found");
                    conf.end_msg( android_proj_node.relpath(),"GREEN")
                else :
                    conf.end_msg("failed","RED")
                    conf.fatal("Command Output : \n" + out + "Error :\n" + err)
        else :
            conf.end_msg("ok","GREEN")
  
        #find assets/www dir
        assetswww_dir = android_proj_node.find_dir('assets').find_dir('www')
        if assetswww_dir is None : conf.fatal("assets/www subfolder was not found. Cannot continue.")
        #cleaning basic cordova project for automatically added items and for old build item
        #TODO what about ? '*.html', '*.txt', '*.php', '*.md', '*.php5', '*.asp', '.htaccess', '.ico'
        #TODO why not delete everything except cordova.js (and maybe master.css) ?
        #TODO what if we need cordova.js in the project use ??
        for todel in ['css','img','images','js','scripts','fonts','audio','content','res','spec','index.html','main.js','spec.html']:
          delnode = assetswww_dir.find_node(todel)
          if delnode is not None :
              if os.path.isdir(delnode.relpath()) : 
                  shutil.rmtree(delnode.relpath(),True)
                  if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION)
              elif os.path.isfile(delnode.relpath()) :
                  os.remove(delnode.relpath())
    
    elif conf.env.PLATFORM == 'chrome' :
        #TODO create a proj_node like for android for easiest computation
        #TODO create default manifest and _locales folder when not found
        pass

    # end of conf.env.PLATFORM handling


    #running configure in tools
    depnode= conf.path.find_dir('tools')
    if depnode is not None : conf.recurse('tools')

    #configuring env for this platform ( one per build variant )
    conf.setenv('debug')
    conf.env.ENGINE=conf.options.engine
    conf.setenv('release')
    conf.env.ENGINE=conf.options.engine
    #configuring env for this platform ( one per build variant )
    # printing all variables setup (for debug)
    #print(conf.env)


def build(bld):

    #save build directory node for build
    bldnode=bld.path.get_bld()
    bldscriptsnode = bldnode.make_node('scripts')
    bldscriptsnode.mkdir()
    chronode = None

    #validate option list
    if bld.options.bT not in BUILDTYPES :
        bld.fatal("The build type " + bld.options.bT + " is unknown. Please use one of those [" + BUILDTYPES +"]")

    #running build in depends
    depends_dir = bld.path.get_src().find_dir('depends')
    if depends_dir is None : bld.fatal("depends/ folder was not found. Cannot continue.")
    else :
        #print depends_dir.abspath()
        bld.recurse('depends')

    #define a portable copy task
    def cp_task(task):
        src = task.inputs[0].abspath()
        tg = task.outputs[0].abspath()
        if os.path.isdir(src) : return shutil.copytree(src,tg)
        elif os.path.isfile(src) : return shutil.copy(src,tg)

    #define an append to eof file task
    def appendToFile_task(task):
        src = task.inputs[0].abspath()
        tg = task.outputs[0].abspath()
        with file(src) as srcf:
            content = srcf.read()
            with open(tg, "a") as tgf:
                tgf.write("\n" + content)

    #define a closure build task
    def cbuild_task(task):
        src = task.inputs[0].abspath()
        tg = task.outputs[0].abspath()
        #TODO
        adv_opti = False; # still buggy
        #(adv_opti is True ? adv = " --compilation_level ADVANCED_OPTIMIZATIONS " : adv = "")
        adv = ""
        if adv_opti is True:
            adv = " --compilation_level ADVANCED_OPTIMIZATIONS "
      
        cbuild_proc = subprocess.Popen(shlex.split("java -jar \"" + bld.env.COMPILER_PATH + "\" " + adv + " --js \"" + src + "\" --js_output_file \"" + tg + "\" --warning_level DEFAULT"),
                cwd=bld.path.get_src().abspath(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = cbuild_proc.communicate()

        if ( cbuild_proc.returncode != 0 ) :
            bld.fatal("Closure Compiler failed. Error : \n" + err)
        else :
            if out is not None and out.strip() != "" :
                print out
            if err is not None and err.strip() != "" :
                print err
        return cbuild_proc.returncode

      
    if bld.env.PLATFORM == 'android' :
        #find publish dir
        pubandroid_dir = bld.path.get_src().find_dir('publish').find_dir('android').find_dir(ANDROID_PROJECT)
        if pubandroid_dir is None : bld.fatal("publish/android/" + ANDROID_PROJECT + " subfolder was not found. Please run waf configure.")
        #find assets/www dir
        assetswww_dir = pubandroid_dir.find_dir('assets').find_dir('www')
        if assetswww_dir is None : bld.fatal("assets/www subfolder was not found. Cannot continue.")
        assetswwwscripts_dir = assetswww_dir.make_node('scripts')
        assetswwwscripts_dir.mkdir()

        if bld.env.ENGINE == "dojo" :
            assetswwwscriptsdojo_dir = assetswwwscripts_dir.make_node("dojo")
            if os.path.exists(assetswwwscriptsdojo_dir.abspath()) :
                shutil.rmtree(assetswwwscriptsdojo_dir.abspath())
                if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION)
            assetswwwscriptsdojo_dir.mkdir()
    #end PLATFORM android
    elif bld.env.PLATFORM == 'chrome' :
        # find chrome_store folder
        chronode = bld.path.get_src().find_dir("publish/chrome_store")
        if chronode is None : # TODO : setup basic chrome_store structure
            bld.fatal("chrome_store not found")
  
    if bld.env.ENGINE == "dojo" : #dojo and web js engine -> just copy files around
        #define how to build app http://livedocs.dojotoolkit.org/build/buildSystem
        def buildApp(profnode, chroEnvNode):
            print "Building " + profnode.relpath()
            bsnode = scripts_dir.find_dir("util/buildscripts") # location of dojo build scripts
            buildprog = "cmd.exe /c build.bat" if (platform.system() == 'Windows') else "sh build.sh"
            app_build_proc = subprocess.Popen(
                shlex.split( buildprog + " -p \"" + profnode.path_from(bsnode) + "\" --bin java --release" ),
                cwd= bsnode.abspath(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            out,err = app_build_proc.communicate()
            if app_build_proc.returncode == 0 :
                if out is not None and out.strip() != "" :
                    print out
                if err is not None and err.strip() != "" :
                    print err

                appBuild_dir = scripts_dir.find_dir(jsOut)

                #concat ENV_FN into build App
                if bld.env.PLATFORM == 'chrome' :
                    if chroEnvNode is not None :
                        chroEnvBuildNode = appBuild_dir.make_node('publish/' + ENV_FN) #build into %appBuild_dir%/publish/
                        print "Building and adding platform env " + chroEnvBuildNode.relpath()
                        bld(
                            rule = cbuild_task,
                            source = chroEnvNode.get_src(),
                            target = chroEnvBuildNode,
                            name = "buildChromeEnv_task"
                        )
                        bld(
                            rule = appendToFile_task,
                            source = chroEnvBuildNode,
                            target = appBuild_dir.find_node('app/app.js'),  #TODO 'app.js' is hard defined, fixed it
                            after = "buildChromeEnv_task",
                            before = "copyBuild_task"
                        )

            else :
                bld.end_msg("failed","RED")
                bld.fatal("Command Output : \n" + out + "Error :\n" + err)

        def cpBuild():
            #look for built result
            appBuild_dir = bld.path.get_src().find_dir('htdocs').find_dir('scripts').find_dir(jsOut)
            dojobuildnode = appBuild_dir.find_dir('dojo')
            if dojobuildnode is None : bld.fatal("Build folder was not found. Cannot continue. TIP: look if java is installed and in the path.")

            #copy built file from build dir to wbuild keeping the structure
            if bld.options.bT == 'debug': #on debug mode we also copy map and uncompressed files
                jsBuildFilesExt = []
                for jsBuildFile in jsBuildFiles:
                    jsBuildFilesExt.extend([jsBuildFile + '.uncompressed.js', jsBuildFile + '.map'])
                jsBuildFiles.extend(jsBuildFilesExt)
            for jsBuildFile in appBuild_dir.get_src().ant_glob(jsBuildFiles): #warning in case a file defined in jsBuildFiles doesnt exists, it will simply be ignore and no message will appear
                print "Extracting " + jsBuildFile.get_src().relpath()
                bld(
                    rule = cp_task,
                    source = jsBuildFile.get_src(),
                    target = bldnode.find_node('scripts').make_node(jsBuildFile.path_from(appBuild_dir)),
                    after = "buildApp"
                )# copy them to the build directory
                if bld.env.PLATFORM == 'android' :
                    bld(
                        rule = cp_task,
                        source = jsBuildFile.get_src(),
                        target = assetswww_dir.find_node('scripts').make_node(jsBuildFile.path_from(appBuild_dir)).get_src(),
                        after = "buildApp",
                        before = "androbuild_task"
                    )

            #extracting dojo resources
            print "Extracting Dojo resources"
            dojoresnode = dojobuildnode.find_dir("resources")
            if dojoresnode is not None :
                scriptsresnode = bldscriptsnode.make_node("dojo").make_node("resources")
                if os.path.exists(scriptsresnode.abspath()) :
                    shutil.rmtree(scriptsresnode.abspath())
                    if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION*5)
                shutil.copytree (dojoresnode.abspath(), scriptsresnode.abspath() )
                if bld.env.PLATFORM == 'android' :
                    shutil.copytree(dojoresnode.abspath(), assetswwwscriptsdojo_dir.make_node("resources").abspath())
        
            if DIJIT :
                #handling Dijit is really there
                dijitbuildnode = appBuild_dir.find_dir('dijit')
                if dijitbuildnode is None : bld.fatal("Built Dijit folder was not found. Cannot continue.")

                #extracting localization resources
                dojonls = dojobuildnode.find_node("nls")
                if dojonls is None : bld.fatal("nls for mandatory base layer was not found in build directory. Cannot continue.")
                print "Extracting Dojo Localization resources"
                bldscriptsdnlsnode = bldscriptsnode.make_node("dojo").make_node("nls")
                bldscriptsdnlsnode.mkdir()
                #copying localization resources from the build ( excluding default copied file by dojo build process )
                for fname in dojonls.ant_glob("dojo_*") :
                    if bld.options.bT == 'debug' or (bld.options.bT != 'debug' and fname.relpath().find("uncompressed.js") == -1 and fname.relpath().find("js.map") == -1) :
                        shutil.copy( fname.abspath(), bldscriptsdnlsnode.abspath())
                        if bld.env.PLATFORM == 'android' :
                            shutil.copytree(bldscriptsdnlsnode.abspath(), assetswwwscriptsdojo_dir.make_node("nls").abspath())
        
                #copying dijit nls as its not working though profile bug #248006
                print "Extracting Dijit Localization resources"
                for dcmpnt in ['dijit/nls/loading.js','dijit/nls/common.js','dijit/form/nls/validate.js','dijit/form/nls/Textarea.js'] : 
                    dcnode = appBuild_dir.get_src().find_node(dcmpnt)
                    if dcnode is None : bld.fatal(os.path.join(appBuild_dir.get_src().relpath(),dcmpnt) + " not found. Aborting.")
                    srccp = dcnode.get_src().abspath()
                    tgtcp = bldscriptsnode.make_node(dcnode.path_from(appBuild_dir)).abspath();
                    if not os.path.exists(os.path.dirname(tgtcp)) :
                        os.makedirs(os.path.dirname(tgtcp))
                    res = shutil.copy(srccp,tgtcp)
                    if bld.env.PLATFORM == 'android' :
                        assetswwwscripts_dir.make_node('dijit/nls').mkdir()
                        assetswwwscripts_dir.make_node('dijit/form/nls').mkdir()
                        shutil.copy(srccp, assetswwwscripts_dir.make_node(dcnode.path_from(appBuild_dir)).abspath())

                #copy built dijit Theme into css
                dijitbuildthemes = dijitbuildnode.find_node("themes")
                if dijitbuildthemes is None : bld.fatal("Dijit themes directory was not found in build directory. Cannot continue.")
                print "Extracting Dijit Themes"
                bldCssNode = bldnode.make_node("css")
                #copying dijit themes (not built)
                for tname in DIJIT_THEMES :
                    _thdir = dijitbuildthemes.find_dir(tname)
                    #print _thdir.abspath()
                    if _thdir is not None :
                        bldCssThNode = bldCssNode.make_node(tname)
                        #print bldCssThNode.abspath()
                        if os.path.exists(bldCssThNode.abspath()) :
                            shutil.rmtree(bldCssThNode.abspath())
                            if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION*10)
                        #print _thdir.find_node(tname + ".css").abspath()
                        #print bldCssThNode.abspath()
                        bldCssThNode.mkdir()
                        shutil.copy(_thdir.find_node(tname + ".css").abspath(), bldCssThNode.abspath() )

                        _thimg = _thdir.find_dir("images")
                        if _thimg is not None :
                            bldCssThImgsNode = bldCssThNode.make_node("images")
                            if os.path.exists(bldCssThImgsNode.abspath()) :
                                shutil.rmtree(bldCssThImgsNode.abspath())
                                if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION)
                            shutil.copytree (_thimg.abspath(), bldCssThImgsNode.abspath() )

                        if bld.env.PLATFORM == 'android' :
                            #print assetswww_dir.make_node("css").make_node(tname).abspath()
                            assetswwwCssThemeNode = assetswww_dir.make_node("css").make_node(tname)
                            if os.path.exists(assetswwwCssThemeNode.abspath()) :
                                shutil.rmtree(assetswwwCssThemeNode.abspath())
                                if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION)
                            shutil.copytree(bldCssThNode.abspath(), assetswwwCssThemeNode.abspath())

            if bld.env.PLATFORM == 'android' :
                #TODO build and copy dojox mobile themes
                pass


        #folder def
        htdocs_dir = bld.path.get_src().find_dir('htdocs')
        if htdocs_dir is None : bld.fatal("htdocs/ subfolder was not found. Cannot continue.")
        scripts_dir = htdocs_dir.find_dir('scripts')
        if scripts_dir is None : bld.fatal("htdocs/scripts subfolder was not found. Cannot continue.")
        app_dir = scripts_dir.find_dir('app')
        if app_dir is None : bld.fatal("htdocs/scripts/app subfolder was not found. Cannot continue.")

        #building app but remove already built first
        profnode = depends_dir.find_node(bld.env.BUILD_PROFILE)
        if profnode is None: bld.fatal("App build profile was not found. Please run waf configure.")
        appBuild_dir = scripts_dir.find_dir(jsOut)
        appIsBuilt = appBuild_dir is not None
        chroEnvNode = chronode.make_node(ENV_FN) if (chronode is not None and chronode.find_node(ENV_FN) is not None) else None
        if bld.options.partial:
            if not appIsBuilt:
                buildApp(profnode, chroEnvNode)
        else:
            if appIsBuilt:
                #print "Removing App build folder"
                shutil.rmtree(appBuild_dir.abspath())
                if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION*150) #folder w numerous files, needs a lot of time to be properly removed
            buildApp(profnode, chroEnvNode)
        
        #static files
        statics = ['images/**/*.png', 'images/**/*.gif', 'images/**/*.jpg', 'images/**/*.jpeg', 'images/**/*.svg',
                   'fonts/*.otf', 'fonts/*.ttf', 'fonts/*.svg', 'fonts/*.eot', 'fonts/*.txt', 'fonts/.htaccess',
                   'css/*.css',
                   'content/*.*',
                   'audio/**/*.ogg', 'audio/**/*.mp3', 'audio/**/*.wav',
                   '*.html', '*.txt', '*.php', '*.md', '*.php5', '*.asp', '.htaccess', '.ico']
        for static in htdocs_dir.get_src().ant_glob(statics): # find them
            if static.relpath().find(".*ignore") == -1 and static.relpath().find("dijit.css") == -1 : #ignoring file w ignore in their name, this also wont copy dir w only an ignore file like a *gitignore ALSO ignoring dijit.css file added by the configure
                bld(
                    rule=cp_task,
                    source=static.get_src(),
                    target=bldnode.make_node(static.path_from(htdocs_dir))
                )# copy them to the build directory
                if bld.env.PLATFORM == 'android' :
                    #copying
                    bld(
                        rule=cp_task,
                        source=bldnode.make_node(static.path_from(htdocs_dir)),
                        target=assetswww_dir.make_node(static.path_from(htdocs_dir))
                    )

        #Compile app src files
        jsFiles = ['*.js']
        if DIJIT:
            jsFiles.extend(['nls/**/*.js'])
        for js in scripts_dir.get_src().ant_glob(jsFiles):
            #print bldscriptsnode.make_node(js.path_from(scripts_dir)).abspath()
            bld(
                rule = cbuild_task,
                source = js.get_src(),
                target = bldscriptsnode.make_node(js.path_from(scripts_dir))
            )
            if bld.env.PLATFORM == 'android' :
                bld(
                    rule = cbuild_task,
                    source = bldscriptsnode.make_node(js.path_from(scripts_dir)),
                    target = assetswwwscripts_dir.make_node(js.path_from(scripts_dir))
                )

        #copy build task call
        cpBuild()

    else : bld.fatal("ENGINE has to be dojo. Please run \'./waf configure [ --engine= [ dojo ] ]\'")
  
    if bld.env.PLATFORM == 'android' : 
        android_pub_node = bld.path.find_node("publish").find_node("android")
        android_proj_node = android_pub_node.find_node(ANDROID_PROJECT);
        # last tuning to make it all work
        #TODO
        # building android version

           
        #define a cordova build task
        def androbuild_task(task):
          src = task.inputs[0].abspath()
          tgt = task.outputs[0].abspath()

          dgbopt = " --release "
          if bld.options.bT == 'debug':
            dbgopt = " --debug "
          
          #finding relevant build script
          buildandroid_node = None
          if os.name == 'posix' and platform.system() == 'Linux':
              buildandroid_node=android_proj_node.find_node("cordova").find_node("build")
              if  buildandroid_node is None : bld.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/build not found.")
              os.chmod(buildandroid_node.abspath(),stat.S_IXUSR | stat.S_IRUSR)
          elif os.name == 'nt' and platform.system() == 'Windows' :
              buildandroid_node=android_proj_node.find_node("cordova").find_node("build.bat")
              if  buildandroid_node is None : bld.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/build.bat not found.")
            
          androbuild_proc = subprocess.Popen(
            buildandroid_node.relpath() + dbgopt ,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True)
          out,err = androbuild_proc.communicate()

          if ( androbuild_proc.returncode != 0 ) :
            bld.fatal("Android Build failed. Error : \n" + err)
          else :
            if out is not None and out.strip() != "" :
              print out
            if err is not None and err.strip() != "" :
              print err
          return androbuild_proc.returncode

        #defining the build task
        bld(
            rule = androbuild_task,
            source = android_proj_node.make_node("build.xml"),
            target = android_proj_node.make_node(os.path.join("ant-build",ANDROID_PROJECT + "-debug.apk" )), #param to check if build is at the good location
            always = True
        )

    elif bld.env.PLATFORM == 'chrome' :
        #manifest version change task
        def mnfst_version_change(task):
            src = task.inputs[0]
            tg = task.outputs[0].abspath()
            #get git commits count http://stackoverflow.com/questions/677436/how-to-get-the-git-commit-count
            git_count_proc = subprocess.Popen(shlex.split("git rev-list HEAD --count"),cwd=bld.path.get_src().abspath(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
            out,err = git_count_proc.communicate()
            if git_count_proc.returncode != 0 : bld.fatal("Cannot determine current git count to set version.")
            else :
                mnfst_str_tmpl = Template(src.read()) # template to do $var based substitution , not to get mixed with json syntax
                mnfst_str = mnfst_str_tmpl.substitute(bzr_rev=out.strip())
            #TODO : handl errors here
            mnfst_bld_file = open(tg,'w')
            mnfst_bld_file.write(mnfst_str)
            mnfst_bld_file.close()
            return 0
            
        #manifest.json needed for chrome
        mnfstnode = chronode.find_node("manifest.json")
        if mnfstnode is None : bld.fatal("manifest.json not found")
        else :
            bld(
                rule=mnfst_version_change,
                source = mnfstnode,
                target = bldnode.make_node(mnfstnode.path_from(chronode))
            )
        
        #copying chrome publish files
        for cpfiles in ['_locales','ico16.png','ico128.png'] :
            cpnode = chronode.get_src().find_node(cpfiles)
            if cpnode is None : bld.fatal(os.path.join(cpnode.get_src().relpath(),cpfiles) + " not found. Aborting.")
            else :
                if os.path.isdir(cpnode.abspath()) :
                    bld_cpnode = bldnode.make_node(cpnode.path_from(chronode))
                    if os.path.exists(bld_cpnode.abspath()) :
                        shutil.rmtree(bld_cpnode.abspath())
                        if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION * 10) #sleep to allow deletion on Windows
                    res = shutil.copytree(cpnode.get_src().abspath(),bld_cpnode.abspath())
                else :
                    srccp = cpnode.get_src().abspath();
                    tgtcp = bldnode.make_node(cpnode.path_from(chronode)).abspath();
                    if not os.path.exists(os.path.dirname(tgtcp)) :
                        os.makedirs(os.path.dirname(tgtcp))
                    res = shutil.copy(srccp,tgtcp)
        return res

def doc(bld):
    """automatically generates the documentation with jsdoc"""
    #TODO : detection of jsdoc in the configuration
    #TODO : generation of the doc during the build, one file at a time with proper dependency...
    #TODO : auto display of the doc in a browser after generation
    bldnode = bld.path.get_bld().find_node(bld.env.PORT)
    if bldnode is None : bld.fatal(bld.env.PORT + " build directory not found. Please run ./waf build again.")
    print bldnode.abspath()

    def docgen_task(task):
        #src = task.inputs[0].abspath()
        #tgt = task.outputs[0].abspath()
        cmd = "sh gen_docs.sh"
        print cmd
        docnode = bld.path.get_src().find_dir("doc")
        if docnode is None : bld.fatal("Cannot find doc/ subdirectory. doc generation aborted")
        gendoc_proc = subprocess.Popen(shlex.split(cmd), cwd=docnode.abspath() ,stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out,err = gendoc_proc.communicate()
        if ( gendoc_proc.returncode != 0) :
            if out is not None or err is not None: bld.fatal("Command Output: \n" + out + "Error : \n" + err)
        return gendoc_proc.returncode
        bld(  rule=docgen_task
            #source=  #TODO : file to generate doc from
            #target=  # TODO : where to put generated doc
        )

    
def run(ctx): # this is a buildcontext
  """run the previously built project for that platform ( or emulator)"""
  bldnode = ctx.path.get_bld().find_node(ctx.env.PORT)
  if bldnode is None : ctx.fatal(ctx.env.PORT + " build directory not found. Please run ./waf build again.")
  #print bldnode.abspath()

  if ctx.env.PLATFORM == 'android' : 
    android_pub_node = ctx.path.find_node("publish").find_node("android")
    android_proj_node = android_pub_node.find_node(ANDROID_PROJECT);
        
    if os.name == 'posix' and platform.system() == 'Linux':
        runandroid_node=android_proj_node.find_node("cordova").find_node("run")
        if runandroid_node is None : ctx.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/run not found.")
        os.chmod(runandroid_node.abspath(),stat.S_IXUSR | stat.S_IRUSR)
    elif os.name == 'nt' and platform.system() == 'Windows' :
        runandroid_node=android_proj_node.find_node("cordova").find_node("run.bat")
        if  runandroid_node is None : ctx.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/run.bat not found.")
            
    androrun_proc = subprocess.Popen(
      runandroid_node.relpath(),
      stdout=subprocess.PIPE,
      stderr=subprocess.PIPE,
      shell=True)
    out,err = androrun_proc.communicate()

    if ( androrun_proc.returncode != 0 ) :
      ctx.fatal("Android Run failed. Error : \n" + err)
    else :
      if out is not None and out.strip() != "" :
        print out
      if err is not None and err.strip() != "" :
        print err


  #TODO : fix / update this
  if ctx.env.PORT == "fdweb" or ctx.env.PORT == "local" :
    #define a task to run firefox
    def firefox_task(task):
      src = task.inputs[0].abspath()
      cmd = "firefox " + os.path.split(src)[1]
      wd = os.path.split(src)[0]
      #print wd, cmd
      #ctx.start_msg(cmd)
      ff_proc = subprocess.Popen(cmd,cwd=wd,shell=True)
      ff_proc.wait()
      #ctx.end_msg( "ok" if ff_proc.returncode == 0 else "failed" )
      if ( ff_proc.returncode != 0) :
        ctx.fatal("Error : the execution of the program in firefox failed")
      return ff_proc.returncode

    startnode = bldnode.find_node(APPNAME+".html")
    #TODO : better than that, handle dependency between here and build
    if startnode is None : ctx.fatal(bldnode.bldpath() + os.sep + APPNAME+".html not found. Please run ./waf build again.")
    else : ctx( rule=firefox_task,
        source=startnode
      )
    
    #TODO : check how to finish waf before running stuff here ( run is not a test, just a help function to run with proper parameters )

  elif ctx.env.PORT == "chrome" :
    #define a task to run chrome
    def chrome_task(task):
      src = task.inputs[0].abspath()
      cmd = "chromium-browser " + os.path.split(src)[1] + " --allow-file-access-from-files"
      wd = os.path.split(src)[0]
      #print wd, cmd
      #ctx.start_msg(cmd)
      chr_proc = subprocess.Popen(cmd,cwd=wd,shell=True)
      chr_proc.wait()
      #ctx.end_msg( "ok" if chr_proc.returncode == 0 else "failed" )
      if ( chr_proc.returncode != 0) :
        ctx.fatal("Error : the execution of the program in chrome failed")
      return chr_proc.returncode

    startnode = bldnode.find_node(APPNAME+".html")
    #TODO : better than that, handle dependency between here and build
    if startnode is None : ctx.fatal(bldnode.bld_path() + os.sep + APPNAME+".html not found. Please run ./waf build again.")
    else : ctx( rule = chrome_task,
        source = startnode
      )

    #TODO : check how to finish waf before running stuff here ( run is not a test, just a help function to run with proper parameters )
  
  elif ctx.env.PORT == "chrome" :
    #define a task to run chrome
    #TODO : run on device ( or emulator ) via cordova
    pass  
    
    
def dist(ctx):
  """package the build result to be delivered to the platform ( local )"""
  ctx.base_name = ctx.get_base_name() + "_local"
  ctx.algo      = 'zip'
  ctx.excl      = ' **/.waf-1* **/*~ **/*.pyc **/*.swp **/.lock-w* **/.bzr **/.svn **/*.waf* **/*.uncompressed.js **/*.log'
  ctx.files     = ctx.path.ant_glob('wbuild/')

def dist_chrome(ctx):
  """package the build result to be delivered to the platform (chrome_store)"""
  ctx.base_name = ctx.get_base_name() + "_chrome"
  ctx.algo      = 'zip'
  ctx.excl      = ' **/.waf-1* **/*~ **/*.pyc **/*.swp **/.lock-w* **/.bzr **/.svn **/*.waf* **/*.uncompressed.js'
  ctx.files     = ctx.path.ant_glob('wbuild/,publish/chrome_store/')

def dist_owa(ctx):
  """package the build result to be delivered to the platform (owa)"""
  ctx.base_name = ctx.get_base_name() + "_owa"
  ctx.algo      = 'zip'
  ctx.excl      = ' **/.waf-1* **/*~ **/*.pyc **/*.swp **/.lock-w* **/.bzr **/.svn **/*.waf* **/*.uncompressed.js'
  ctx.files     = ctx.path.ant_glob('wbuild/,publish/owa_store/')

  #https://code.google.com/p/waf/wiki/WafDist

  
#TODO : distcheck : run tests on packaged app

###################### WAF trick section #################################################
from waflib.Build import BuildContext, CleanContext, InstallContext, UninstallContext
## to support multiple variants
#for x in 'debug release'.split():
# for y in (BuildContext, CleanContext, InstallContext, UninstallContext):
#   name = y.__name__.replace('Context','').lower()
#   class tmp(y):
#     cmd = name + '_' + x
#     variant = x

### to be able to have a doc function that get context from build
class doc_class(BuildContext):
  cmd = 'doc'
  fun = 'doc'

from waflib.Task import Task
### example :
#class cp(Task):
#        def run(self):
#                return self.exec_command('cp %s %s' % (
#                                self.inputs[0].abspath(),
#                                self.outputs[0].abspath()
#                        )
#                )

### to be able to have a run function that get context from build
class run_class(BuildContext):
  cmd = 'run'
  fun = 'run'
### to be able to run debug or release variants
#for x in 'debug release'.split():
# class run_class_vart(BuildContext):
#   cmd = 'run_' + x
#   fun = 'run'
#   variant = x

from waflib.Scripting import Dist
## to support multiple dist variants ( used for platform specific dists)
for x in 'chrome owa'.split():
  name = Dist.__name__.lower()
  class tmp(Dist):
    cmd = name + '_' + x
    fun = name + '_' + x
    variant = x

