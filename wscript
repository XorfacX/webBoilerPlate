# How to use
# ==========
#   ./waf configure --download --engine=[dojo] --platform=[android|local|chrome|owa]
#   ./waf build --partial --bT=[debug|release]
#   ./waf install
#   ./waf dist_[chrome]


import sys
import os
import stat
import shutil
import urllib
import zipfile
import shlex
import subprocess
import multiprocessing
import json
from string import Template
import platform
import time

APPNAME = 'webBoilerPlate' #set Your Project Name Here
VERSION = '1' #set Your Project Version Here (only used internally by waf on build)

ANDROID_PACKAGE = "com.fairydwarves.webboilerplate" #set your android package identifier when applicable
ANDROID_PROJECT = "webBoilerPlate" #set your android app name when applicable

DIJIT = 1 #do we use dijit ?
DIJIT_THEMES = ['nihilo'] #set the list of dijit themes we want to build

BUILDTYPES = 'debug release'
ENV_FN = 'Environment.js' #platform env file

top = '.'
out = 'wbuild'
jsOut = '_release' #JS build folder name
jsBuildFiles = ['app/app.js', 'dojo/dojo.js'] #results of JS build: add other built files you want to copy here
cssBuildFiles = ['css/general.css'] #results of CSS build: add other built files you want to copy here


def options(opt):
    """ Defines which option can be used for this project """
    opt.recurse('depends')
    opt.recurse('tools')
    
    opt.add_option('--partial', action='store_true', default=False, help='do not rebuild the app if build folder is present [True | False (default)')

    opt.add_option('--bT', action='store', default='debug', help='build type [debug (default)| release ]')

def configure(conf):
    conf.check_waf_version(mini='1.6.3')

    #running configure in depends
    depends_dir = conf.path.find_dir('depends')
    if depends_dir is not None : conf.recurse('depends')

    # Finding the htdocs folder, the root
    htdocsnode = conf.path.find_dir('htdocs')
    if htdocsnode is None : conf.fatal("htdocs/ subfolder was not found. Cannot continue.")
    
    # Finding the scripts folder where to put build results
    scriptsnode = htdocsnode.find_dir('scripts')
    if scriptsnode is None : conf.fatal("htdocs/scripts/ subfolder was not found. Cannot continue.")

    #copying depends single files and folders content
    for depend in conf.env.DEPENDS:
        dependNode = depends_dir.find_node(depend)
        if dependNode is None: conf.fatal(depend + " was not found. Please run waf configure --download.")
        #else: print depend + " path " + dependNode.abspath()

        if os.path.isdir(dependNode.abspath()) : #FOLDER HANDLING
            conf.start_msg("Retrieving " + depend)
            files = os.listdir(dependNode.abspath())
            for file in files:
                src_file = os.path.join(dependNode.abspath(), file)
                dst_file = os.path.join(scriptsnode.abspath(), file)
                removeLoc(dst_file)
                shutil.move(src_file, dst_file)
            conf.end_msg(scriptsnode.relpath() + " : [" + ', '.join(files) + "]")
        else : #FILE HANDLING
            conf.start_msg("Retrieving " + depend)
            shutil.copy(dependNode.abspath(),scriptsnode.abspath())
            conf.end_msg(scriptsnode.find_node(os.path.basename(dependNode.abspath())).relpath())

    #handling ENGINE
    if conf.env.ENGINE == "dojo":
        # Copying doh for testing purposes into our tests directory
        if scriptsnode.find_dir('app') is not None : #todo hard coded name, fixed it
            testsnode = scriptsnode.find_dir('app').find_dir('tests')
            if testsnode is not None :
                dohnode = scriptsnode.find_dir('util/doh')
                if dohnode is None : conf.fatal("util/doh subfolder was not found in dojo directory. Cannot continue.")
  
                dohdstnode = testsnode.make_node('doh')
                conf.start_msg("Copying " + dohnode.relpath() + " to " + dohdstnode.relpath())
                removeLoc(dohdstnode.relpath())
                shutil.copytree(dohnode.relpath(), dohdstnode.relpath())
                conf.end_msg("ok")
            #else: conf.fatal("tests/ subfolder was not found. Cannot continue.")

    else: # no need of dojo
        pass
    #end of conf.env.ENGINE

    #handling PLATFORM
    if conf.env.PLATFORM == 'android' :
        android_pub_node = conf.path.find_node("publish").find_node("android")
        if android_pub_node is None : conf.fatal("Cannot find publish/android path")

        android_proj_node = android_pub_node.find_node(ANDROID_PROJECT)
        if android_proj_node is None :
            conf.end_msg("failed","RED")

            conf.start_msg("Creating Cordova Project")
            cordova_create_proc = subprocess.Popen("cordova create \"" + os.path.join(android_pub_node.path_from(conf.path),ANDROID_PROJECT) + "\" \"" + ANDROID_PACKAGE + "\" \"" + ANDROID_PROJECT + "\"",
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
            out,err = cordova_create_proc.communicate()
            if cordova_create_proc.returncode == 0 :
                conf.to_log(out)
                conf.to_log(err)
                android_proj_node = android_pub_node.find_node(ANDROID_PROJECT)
                if android_proj_node is None : conf.fatal(ANDROID_PROJECT + " was not found")
                conf.end_msg(android_proj_node.relpath(),"GREEN")
            else :
                conf.end_msg("failed","RED")
                conf.fatal("Command Output : \n" + out + "Error :\n" + err)
    
    elif conf.env.PLATFORM == 'chrome' :
        #TODO create a proj_node like for android for easiest computation
        #TODO create default manifest and _locales folder when not found
        pass

    elif conf.env.PLATFORM == 'facebook' :
        #TODO create a proj_node like for android for easiest computation
        #TODO create default manifest and _locales folder when not found
        pass

    # end of conf.env.PLATFORM handling


    #running configure in tools
    depnode = conf.path.find_dir('tools')
    if depnode is not None : conf.recurse('tools')

    #configuring env for this platform ( one per build variant )
    conf.setenv('debug')
    conf.env.ENGINE = conf.options.engine
    conf.setenv('release')
    conf.env.ENGINE = conf.options.engine
    #configuring env for this platform ( one per build variant )
    # printing all variables setup (for debug)
    #print(conf.env)


def build(bld):

    #save build directory node for build
    bldnode = bld.path.get_bld()
    bldscriptsnode = bldnode.make_node('scripts')
    bldscriptsnode.mkdir()

    #platform specifics
    chronode = None
    fbnode = None

    #validate option list
    if bld.options.bT not in BUILDTYPES :
        bld.fatal("The build type " + bld.options.bT + " is unknown. Please use one of those [" + BUILDTYPES + "]")

    #running build in depends
    depends_dir = bld.path.get_src().find_dir('depends')
    if depends_dir is None : bld.fatal("depends/ folder was not found. Cannot continue.")
    else :
        #print depends_dir.abspath()
        bld.recurse('depends')

    #define a portable copy task
    #WARNING when using this task files are not copied each build but only the FIRST TIME. if you need to copy them again, you need to do a full distclean before.
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
        adv_opti = False; #still buggy
        #(adv_opti is True ? adv = " --compilation_level ADVANCED_OPTIMIZATIONS " : adv = "")
        adv = ""
        if adv_opti is True:
            adv = " --compilation_level ADVANCED_OPTIMIZATIONS "
        cbuild_cmd = "java -jar \"" + bld.env.COMPILER_PATH + "\" " + adv + " --js \"" + src + "\" --js_output_file \"" + tg + "\" --warning_level DEFAULT" 
        #print "Calling Closure Compiler : " + cbuild_cmd
        cbuild_proc = subprocess.Popen(shlex.split(cbuild_cmd),
                cwd=bld.path.get_src().abspath(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = cbuild_proc.communicate()

        if (cbuild_proc.returncode > 0) :
            bld.fatal("Closure Compiler failed. Error : \n" + err)
        else :
            if out is not None and out.strip() != "" :
                print out
            if err is not None and err.strip() != "" :
                print err
        return cbuild_proc.returncode

    #manifest/config/... version set task
    def version_set(task):
        src = task.inputs[0]
        tg = task.outputs[0].abspath()
        #get git commits count http://stackoverflow.com/questions/677436/how-to-get-the-git-commit-count
        git_count_proc = subprocess.Popen(shlex.split("git rev-list HEAD --count"),cwd=bld.path.get_src().abspath(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        out,err = git_count_proc.communicate()
        if git_count_proc.returncode != 0 : bld.fatal("Cannot determine current git count to set version.")
        else :
            versionStr = Template(src.read()).substitute({'version': VERSION + "." + out.strip(), 'androVersion': VERSION.replace('.', '') + out.strip()})  #replace $version w VERSION.build and androVersion w VERSION (wo dots) + build
        #TODO : handle errors here
        version_file = open(tg,'w')
        version_file.write(versionStr)
        version_file.close()
        return 0

    if bld.env.PLATFORM == 'chrome' :
        # find chrome_store folder
        chronode = bld.path.get_src().find_dir("publish/chrome_store")
        if chronode is None : # TODO : setup basic chrome_store structure
            bld.fatal("chrome_store not found")

    elif bld.env.PLATFORM == 'facebook' :
        # find chrome_store folder
        fbnode = bld.path.get_src().find_dir("publish/facebook")
        if fbnode is None : # TODO : setup basic facebook structure
            bld.fatal("fbnode not found")
  
    if bld.env.ENGINE == "dojo" : #dojo and web js engine -> just copy files around
        #define how to build app http://livedocs.dojotoolkit.org/build/buildSystem
        def buildApp(profnode, chroEnvNode):
            print "Building " + profnode.relpath()
            bsnode = scripts_dir.find_dir("util/buildscripts") # location of dojo build scripts
            buildprog = "cmd.exe /c build.bat" if (platform.system() == 'Windows') else "sh build.sh"
            buildcmd = buildprog + " -p \"" + profnode.path_from(bsnode) + "\" --bin java --release"
            print "Build command : " + buildcmd
            app_build_proc = subprocess.Popen(shlex.split(buildcmd),
                cwd= bsnode.abspath(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)
            out,err = app_build_proc.communicate()
            if app_build_proc.returncode == 0 :
                if out is not None and out.strip() != "" :
                    print out
                if err is not None and err.strip() != "" :
                    print err

                appBuild_dir = scripts_dir.find_dir(jsOut)

                #concat ENV_FN into build App
                if bld.env.PLATFORM == 'chrome' or bld.env.PLATFORM == 'facebook':
                    if platfEnvNode is not None :
                        platfEnvBuildNode = appBuild_dir.make_node('publish/' + ENV_FN) #build into %appBuild_dir%/publish/
                        print "Building and adding platform env " + platfEnvBuildNode.relpath()

                        bld(rule = cbuild_task,
                            source = platfEnvNode.get_src(),
                            target = platfEnvBuildNode,
                            name = "buildPlatfEnv_task")

                        bld(rule = appendToFile_task,
                            source = platfEnvBuildNode,
                            target = appBuild_dir.find_node('app/app.js'),  #TODO 'app.js' is hard defined, fixed it
                            after = "buildPlatfEnv_task",
                            before = "cpBuild")

            else :
                bld.fatal("Command Output : \n" + out + "Error :\n" + err)

        def cpBuild():
            #look for built result
            appBuild_dir = bld.path.get_src().find_dir('htdocs').find_dir('scripts').find_dir(jsOut)
            dojobuildnode = appBuild_dir.find_dir('dojo')
            if dojobuildnode is None : bld.fatal("Build folder was not found. Cannot continue. TIP: look if java is installed and in the path.")

            #copy built files (js + css) from build dir to wbuild keeping the structure
            if bld.options.bT == 'debug': #on debug mode we also copy map and uncompressed files
                jsBuildFilesExt = []
                for jsBuildFile in jsBuildFiles:
                    jsBuildFilesExt.extend([jsBuildFile + '.uncompressed.js', jsBuildFile + '.map'])
                jsBuildFiles.extend(jsBuildFilesExt)
            for jsBuildFile in appBuild_dir.get_src().ant_glob(jsBuildFiles): #warning in case a file defined in jsBuildFiles doesnt exists, it will simply be ignore and no message will appear
                print "Extracting " + jsBuildFile.get_src().relpath() + " to " + bldnode.find_node('scripts').make_node(jsBuildFile.path_from(appBuild_dir)).abspath()
                bld(rule = cp_task,
                    source = jsBuildFile.get_src(),
                    target = bldnode.find_node('scripts').make_node(jsBuildFile.path_from(appBuild_dir)),
                    after = "buildApp",
                    before = "AppBuildToCordovaCopy_task") #copy them to the build directory
            for cssBuildFile in appBuild_dir.get_src().ant_glob(cssBuildFiles): #warning in case a file defined in cssBuildFiles doesnt exists, it will simply be ignore and no message will appear
                print "Extracting " + cssBuildFile.get_src().relpath() + " to " + bldnode.make_node(cssBuildFile.path_from(appBuild_dir)).abspath()
                bld(rule = cp_task,
                    source = cssBuildFile.get_src(),
                    target = bldnode.make_node(cssBuildFile.path_from(appBuild_dir)),
                    after = "buildApp",
                    before = "AppBuildToCordovaCopy_task") #copy them to the build directory
              

            #extracting dojo resources
            print "Extracting Dojo resources"
            dojoresnode = dojobuildnode.find_dir("resources")
            if dojoresnode is not None :
                scriptsresnode = bldscriptsnode.make_node("dojo").make_node("resources")
                removeLoc(scriptsresnode.abspath())
                shutil.copytree(dojoresnode.abspath(), scriptsresnode.abspath())

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
                        shutil.copy(fname.abspath(), bldscriptsdnlsnode.abspath())

                #extracting app localization resources if applicable (TODO: those files are compiled since dojo 1.10 under an app_%locale%.js filename, what should we do w it?)
                appnls = appBuild_dir.find_node("app/nls/")
                if appnls is not None :
                    print "Extracting App Localization resources"
                    bldscriptsdnlsnode = bldscriptsnode.make_node("app").make_node("nls")
                    bldscriptsdnlsnode.mkdir()
                    #copying localization resources from the build
                    for fname in appnls.ant_glob(["**/*"]) :
                        if bld.options.bT == 'debug' or (bld.options.bT != 'debug' and fname.relpath().find("uncompressed.js") == -1 and fname.relpath().find("js.map") == -1) :
                            bld(rule=cp_task,
                                source=fname.get_src(),
                                target=bldscriptsdnlsnode.make_node(fname.path_from(appnls)),
                                before = "AppBuildToCordovaCopy_task")
                    
                #copy built dijit Theme into css
                dijitbuildthemes = dijitbuildnode.find_node("themes")
                if dijitbuildthemes is None : bld.fatal("Dijit themes directory was not found in build directory. Cannot continue.")
                print "Extracting Dijit Themes"
                bldDijitThemesNode = bldnode.make_node("dijit").make_node("themes")
                removeLoc(bldDijitThemesNode.abspath())
                #copying dijit themes (not built)
                for tname in DIJIT_THEMES :
                    _thdir = dijitbuildthemes.find_dir(tname)
                    #print _thdir.abspath()
                    if _thdir is not None :
                        bldDijitThemesThNode = bldDijitThemesNode.make_node(tname)
                        bldDijitThemesThNode.mkdir()
                        _thimg = _thdir.find_dir("images")
                        if _thimg is not None :
                            bldDijitThemesImgsNode = bldDijitThemesThNode.make_node("images")
                            #removeLoc(bldCssThImgsNode.abspath())
                            shutil.copytree(_thimg.abspath(), bldDijitThemesImgsNode.abspath())


        #folder def
        htdocs_dir = bld.path.get_src().find_dir('htdocs')
        if htdocs_dir is None : bld.fatal("htdocs/ subfolder was not found. Cannot continue.")
        scripts_dir = htdocs_dir.find_dir('scripts')
        if scripts_dir is None : bld.fatal("htdocs/scripts subfolder was not found. Cannot continue.")
        app_dir = scripts_dir.find_dir('app')
        if app_dir is None : print "Notice: htdocs/scripts/app subfolder not found. Switching to irregular folder archi mode."

        #building app but remove already built first
        profnode = depends_dir.find_node(bld.env.BUILD_PROFILE)
        if profnode is None: bld.fatal("App build profile was not found. Please run waf configure.")
        appBuild_dir = scripts_dir.find_dir(jsOut)
        appIsBuilt = appBuild_dir is not None

        platfEnvNode = None
        if bld.env.PLATFORM == 'chrome' :
            platfEnvNode = chronode.make_node(ENV_FN) if (chronode is not None and chronode.find_node(ENV_FN) is not None) else None
        elif bld.env.PLATFORM == 'facebook':
            platfEnvNode = fbnode.make_node(ENV_FN) if (fbnode is not None and fbnode.find_node(ENV_FN) is not None) else None

        if bld.options.partial:
            if not appIsBuilt:
                buildApp(profnode, platfEnvNode)
        else:
            if appIsBuilt:
                #print "Removing App build folder"
                removeLoc(appBuild_dir.abspath())
            buildApp(profnode, platfEnvNode)
        
        #static files
        statics = ['images/**/*.png', 'images/**/*.gif', 'images/**/*.jpg', 'images/**/*.jpeg', 'images/**/*.svg',
                   'fonts/*.otf', 'fonts/*.ttf', 'fonts/*.svg', 'fonts/*.eot', 'fonts/*.txt', 'fonts/.htaccess',
                   'content/**/*', 'scripts/*.json',
                   'audio/**/*.ogg', 'audio/**/*.mp3', 'audio/**/*.wav', 'audio/**/*.aac',
                   '*.html', '*.txt', '*.php', '*.md', '*.php5', '*.asp', '.htaccess', '*.ico']
        for static in htdocs_dir.get_src().ant_glob(statics): # find them
            if static.relpath().find(".*ignore") == -1 and static.relpath().find("dijit.css") == -1 : #ignoring file w ignore in their name, this also wont copy dir w only an ignore file like a *gitignore ALSO ignoring dijit.css file added by the configure
                bld(rule=cp_task,
                    source=static.get_src(),
                    target=bldnode.make_node(static.path_from(htdocs_dir)),
                    before = "AppBuildToCordovaCopy_task") #copy them to the build directory
                
        #Compile app external src files
        jsFiles = ['*.js']
        if DIJIT:
            jsFiles.extend(['nls/**/*.js'])
        for js in scripts_dir.get_src().ant_glob(jsFiles):
            #print bldscriptsnode.make_node(js.path_from(scripts_dir)).abspath()
            bld(rule = cbuild_task,
                source = js.get_src(),
                target = bldscriptsnode.make_node(js.path_from(scripts_dir)),
                before = "AppBuildToCordovaCopy_task")


        #copy build task call
        cpBuild()

    else : bld.fatal("ENGINE has to be dojo. Please run \'./waf configure [ --engine= [ dojo ] ]\'")

    if bld.env.PLATFORM == 'android' : #TODO: continue w others cordova handled platform

        #add platform to cordova list of platforms task
        def cordovaAddPlatform_task(task):
            cordova_android_proc = subprocess.Popen("cordova platform add " + bld.env.PLATFORM,
                cwd=cordova_proj_node.relpath(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
            out,err = cordova_android_proc.communicate()
            if cordova_android_proc.returncode == 0 :
                if out is not None and out.strip() != "" :
                    print out
                if err is not None and err.strip() != "" :
                    print err
                android_plat_node = (cordova_proj_node.find_node("platforms") and cordova_proj_node.find_node("platforms").find_node("android"))
                if android_plat_node is None : bld.fatal("platforms/" + bld.env.PLATFORM + " was not found")                
            else :
                print "Failed: Command Output : \n" + out + "Error :\n" + err
            return 0

        #clean cordova platform from existing files
        def cordovaCleanPlatform_task(task):
            toRemove = ['www/**/*', 'platforms/' + bld.env.PLATFORM +'/assets/www/**/*']
            for toRemoveEl in cordova_proj_node.ant_glob(toRemove, dir=True, excl=['**/cordova*.js']): # find them incl directories and ignoring cordova files
                if os.path.isdir(toRemoveEl.relpath()) :
                    removeLoc(toRemoveEl.relpath())
                elif os.path.isfile(toRemoveEl.relpath()) :
                    os.remove(toRemoveEl.relpath())
            return 0

        #define a copy from built app to cordova task
        def appbuildtocordovacopy_task(task):
            for toCopyEl in bldnode.ant_glob('*', file=True, dir=True, excl=['c4che', '.lock*', '.waf*', 'config.log']): #copy all except waf build files
                toCopyNode = cordovawww_dir.make_node(toCopyEl.bldpath())
                print "Copying " + toCopyEl.abspath() + " => " + toCopyNode.abspath()
                if os.path.isdir(toCopyEl.abspath()) :
                    removeLoc(toCopyNode.abspath())
                    shutil.copytree(toCopyEl.abspath(), toCopyNode.abspath())
                elif os.path.isfile(toCopyEl.abspath()) :
                    shutil.copy(toCopyEl.abspath(), cordovawww_dir.abspath())
            return 0

        #define a cordova platform update task
        def cordovaplatformupdate_task(task):
            cordovaplatformupdate_proc = subprocess.Popen("cordova platform update " + bld.env.PLATFORM,
                cwd=cordova_proj_node.relpath(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
            out,err = cordovaplatformupdate_proc.communicate()

            if (cordovaplatformupdate_proc.returncode != 0) :
                print bld.env.PLATFORM + " build failed. Fatal Error: \n" + err
            else :
                if out is not None and out.strip() != "" :
                    print out
                if err is not None and err.strip() != "" :
                    print err
            return cordovaplatformupdate_proc.returncode
            
        #define a cordova build task
        def androbuild_task(task):
            dbgopt = " --debug "
            if bld.options.bT == 'release':
                dbgopt = " --release "
            
            #copy build.json to cordova project
            buildJsonNode = android_pub_node.find_node("build.json")
            if buildJsonNode is not None :
                shutil.copy(buildJsonNode.abspath(),cordova_proj_node.abspath())

            #TODO: when and how do we clean platforms/%PLATFORM%/ant-build from older and other build type builds ???
            androbuild_proc = subprocess.Popen("cordova build " + dbgopt + " android" + (" --buildConfig=build.json" if (buildJsonNode is not None) else ""),
                cwd=cordova_proj_node.relpath(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=True)
            out,err = androbuild_proc.communicate()

            if (androbuild_proc.returncode != 0) :
                bld.fatal("Android Build failed. Error : \n" + err)
            else :
                if out is not None and out.strip() != "" :
                    print out
                if err is not None and err.strip() != "" :
                    print err
            return androbuild_proc.returncode
        

        #folders checks/setup
        android_pub_node = bld.path.find_node("publish").find_node("android")
        if android_pub_node is None : bld.fatal("publish/android/ subfolder was not found. Please fix.")
        cordova_proj_node = android_pub_node.find_node(ANDROID_PROJECT)
        if cordova_proj_node is None : bld.fatal("publish/android/" + ANDROID_PROJECT + " subfolder was not found. Please run waf configure first.")
        cordovawww_dir = cordova_proj_node.find_dir('www')

        #Set version and copy config.xml if existing into ANDROID_PROJECT to replace default one
        configXmlNode = android_pub_node.find_node("config.xml")
        if configXmlNode is None : bld.fatal("config.xml not found")
        else :
            bld(rule=version_set,
                always = True,
                source = configXmlNode,
                target = cordova_proj_node.make_node(configXmlNode.path_from(android_pub_node)),
                name = "VersionSet_task",
                before = "CordovaAddPlatform_task")

        #add android platform
        android_plat_node = (cordova_proj_node.find_node("platforms") and cordova_proj_node.find_node("platforms").find_node("android"))
        if android_plat_node is None :
             bld(rule = cordovaAddPlatform_task,
                always = True,
                name = "CordovaAddPlatform_task",
                before = "CordovaCleanPlatform_task")

        #find existing www & assets/www dir and clean them
        #TODO what if we need cordova.js in the project use ?? => we would need our cordova root to be the same has our git root and cordova/www must be configured to be called htdocs i guess (there is no way we change all our project folder names from htdocs to www). Otherwise we would have to copy cordova.js and cordova_plugins.js into htdocs but it must be done on configure and i dont think they're ready untill build time.
        bld(rule = cordovaCleanPlatform_task,
            always = True,
            name = "CordovaCleanPlatform_task",
            before = "pkgFilesCopy_task")
        #TODO : this should be handled by clean(invert of build) or distclean ( invert of configure )
        
        #copying publish package files #TODO: maybe this (icons, splashScreens copy to wbuild) is not needed because those files seems to be added to the built apk anyway TBT
        for pkgFile in android_pub_node.get_src().ant_glob(['icons/**/*','splashScreens/**/*']): # find them
            bld(rule=cp_task,
                source=pkgFile.get_src(),
                target=bldnode.make_node(pkgFile.path_from(android_pub_node)),
                name = "pkgFilesCopy_task",
                before = "AppBuildToCordovaCopy_task") #copy them to the build directory

        #cordova platform: copy wbuild, update then build
        bld(rule = appbuildtocordovacopy_task,
            always = True,
            name = "AppBuildToCordovaCopy_task",
            before = "CordovaPlatformUpdate_task")

        bld(rule = cordovaplatformupdate_task,
            always = True,
            name = "CordovaPlatformUpdate_task",
            before = "androbuild_task",
            after = "AppBuildToCordovaCopy_task")

        bld(rule = androbuild_task,
            source = cordova_proj_node.make_node("config.xml"),
            always = True,
            name = "androbuild_task",
            after = "CordovaPlatformUpdate_task")
    #END ANDROID PLATFORM

    elif bld.env.PLATFORM == 'chrome' :
            
        #manifest.json needed for chrome
        mnfstnode = chronode.find_node("manifest.json")
        if mnfstnode is None : bld.fatal("manifest.json not found")
        else :
            bld(rule=version_set,
                source = mnfstnode,
                target = bldnode.make_node(mnfstnode.path_from(chronode)))
        
        #copying chrome publish files
        for cpfiles in ['_locales','ico16.png','ico128.png'] :
            cpnode = chronode.get_src().find_node(cpfiles)
            if cpnode is None : bld.fatal(os.path.join(cpnode.get_src().relpath(),cpfiles) + " not found. Aborting.")
            else :
                if os.path.isdir(cpnode.abspath()) :
                    bld_cpnode = bldnode.make_node(cpnode.path_from(chronode))
                    removeLoc(bld_cpnode.abspath())
                    res = shutil.copytree(cpnode.get_src().abspath(),bld_cpnode.abspath())
                else :
                    srccp = cpnode.get_src().abspath()
                    tgtcp = bldnode.make_node(cpnode.path_from(chronode)).abspath()
                    if not os.path.exists(os.path.dirname(tgtcp)) :
                        os.makedirs(os.path.dirname(tgtcp))
                    res = shutil.copy(srccp,tgtcp)
        return res

    elif bld.env.PLATFORM == 'facebook' :
            
        #manifest.json needed for chrome
        mnfstnode = fbnode.find_node("manifest.json")
        if mnfstnode is None : bld.fatal("manifest.json not found")
        else :
            bld(rule=version_set,
                source = mnfstnode,
                target = bldnode.make_node(mnfstnode.path_from(fbnode)))

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
        if (gendoc_proc.returncode != 0) :
            if out is not None or err is not None: bld.fatal("Command Output: \n" + out + "Error : \n" + err)
        return gendoc_proc.returncode
        bld(rule=docgen_task
            #source= #TODO: file to generate doc from
            #target= #TODO: where to put generated doc
        )

    
def run(ctx): # this is a buildcontext
  """run the previously built project for that platform ( or emulator)"""
  bldnode = ctx.path.get_bld().find_node(ctx.env.PORT)
  if bldnode is None : ctx.fatal(ctx.env.PORT + " build directory not found. Please run ./waf build again.")
  #print bldnode.abspath()

  if ctx.env.PLATFORM == 'android' : 
    android_pub_node = ctx.path.find_node("publish").find_node("android")
    android_proj_node = android_pub_node.find_node(ANDROID_PROJECT)

    androrun_proc = subprocess.Popen("cordova run android",
        cwd=android_proj_node.relpath(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        shell=True)
    out,err = androrun_proc.communicate()

    if (androrun_proc.returncode != 0) :
      ctx.fatal("Android Run failed. Error : \n" + err)
    else :
      if out is not None and out.strip() != "" :
        print out
      if err is not None and err.strip() != "" :
        print err


  #TODO : fix / update this
  if ctx.env.PORT == "web" or ctx.env.PORT == "local" or ctx.env.PORT == "facebook":
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
      if (ff_proc.returncode != 0) :
        ctx.fatal("Error : the execution of the program in firefox failed")
      return ff_proc.returncode

    startnode = bldnode.find_node(APPNAME + ".html")
    #TODO : better than that, handle dependency between here and build
    if startnode is None : ctx.fatal(bldnode.bldpath() + os.sep + APPNAME + ".html not found. Please run ./waf build again.")
    else : ctx(rule=firefox_task, #TODO: better, use default OS browser
        source=startnode)
    
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
      if (chr_proc.returncode != 0) :
        ctx.fatal("Error : the execution of the program in chrome failed")
      return chr_proc.returncode

    startnode = bldnode.find_node(APPNAME + ".html")
    #TODO : better than that, handle dependency between here and build
    if startnode is None : ctx.fatal(bldnode.bld_path() + os.sep + APPNAME + ".html not found. Please run ./waf build again.")
    else : ctx(rule = chrome_task,
        source = startnode)

    #TODO : check how to finish waf before running stuff here ( run is not a test, just a help function to run with proper parameters )
    
def dist(ctx):
  """package the build result to be delivered to the platform ( local )"""
  ctx.base_name = ctx.get_base_name() + "_local"
  ctx.algo = 'zip'
  ctx.excl = ' **/.waf-1* **/*~ **/*.pyc **/*.swp **/.lock-w* **/.bzr **/.svn **/*.waf* **/*.uncompressed.js **/*.log'
  ctx.files = ctx.path.ant_glob('wbuild/')

def dist_chrome(ctx):
  """package the build result to be delivered to the platform (chrome_store)"""
  ctx.base_name = ctx.get_base_name() + "_chrome"
  ctx.algo = 'zip'
  ctx.excl = ' **/.waf-1* **/*~ **/*.pyc **/*.swp **/.lock-w* **/.bzr **/.svn **/*.waf* **/*.uncompressed.js'
  ctx.files = ctx.path.ant_glob('wbuild/,publish/chrome_store/')

def dist_owa(ctx):
  """package the build result to be delivered to the platform (owa)"""
  ctx.base_name = ctx.get_base_name() + "_owa"
  ctx.algo = 'zip'
  ctx.excl = ' **/.waf-1* **/*~ **/*.pyc **/*.swp **/.lock-w* **/.bzr **/.svn **/*.waf* **/*.uncompressed.js'
  ctx.files = ctx.path.ant_glob('wbuild/,publish/owa_store/')

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
    
# Remove a location
# In order to be sure it's done, we loop until we can actually recreate it than delete it on last time
def removeLoc(location):
    while 1:
        try:
            if os.path.exists(location):
                shutil.rmtree(location)
            os.makedirs(location)
            break
        except:
            pass

    shutil.rmtree(location)