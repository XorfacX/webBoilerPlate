# How to use
# ==========
# - On Unix
#   > ./waf configure --download --engine=[dojo]
#   > ./waf build [modules / tests] -> TO BE DEFINED
#   > ./waf install
#   > ./waf dist_[chrome]
#
# Concept:
#

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

APPNAME = 'webRoot' #set Your Project Name Here
VERSION = '1' #set Your Project Version Here (only used internally by waf on build)
ENGINES = 'dojo'  #nb: we should think about cleaning this from here or from depends/wscript ...

ANDROID_PACKAGE = "com.fairydwarves.Gamebook" #set your android package identifier when applicable
ANDROID_PROJECT = "FDwebRoot" #set your android app name when applicable


#TODO : find a way to get that from depends/wscript
DOJO_VERSION = "1.9.2"
DOJO_UNZIP = "dojo-release-" + DOJO_VERSION + "-src"
DOJO_PROFILE = "app.profile.js"
DIJIT_THEMES = ['nihilo'] #set the list of dojo themes we want to build

WINDOWS_SLEEP_DURATION = 0.1

top = '.'
out = 'wbuild'


def options(opt):
  """ Defines which option can be used for this project """
  opt.recurse('depends')
  opt.recurse('tools')

def configure(conf):
    conf.check_waf_version(mini='1.6.3')

    #running configure in depends
    depnode= conf.path.find_dir('depends')
    if depnode is not None : conf.recurse('depends')
      
    mdnode = depnode.find_node("Markdown.Converter.js")
    if mdnode is None: conf.fatal("Markdown.Converter.js was not found. Please run waf configure --download.")
    #else: print "markdown.js path " + mdnode.abspath()
    
    # Finding the htdocs folder, the root
    htdocsnode = conf.path.find_dir('htdocs')
    if htdocsnode is None : conf.fatal("htdocs/ subfolder was not found. Cannot continue.")
    
    # Finding the scripts folder where to put build results
    scriptsnode = htdocsnode.find_dir('scripts')
    if scriptsnode is None : conf.fatal("htdocs/scripts/ subfolder was not found. Cannot continue.")
    
    #copying markdown.js
    conf.start_msg("Retrieving markdown.js" )
    shutil.copy(mdnode.abspath(),scriptsnode.abspath())
    conf.end_msg( scriptsnode.find_node(os.path.basename(mdnode.abspath())).relpath())

    if conf.env.ENGINE == "dojo":
        #find dojo directory
        dojonode = depnode.ant_glob(DOJO_UNZIP,src=False, dir=True)[0]
        if dojonode is None: conf.fatal("dojo toolkit was not found. Please run waf configure.")
        #else: print "dojo path " + dojonode.abspath()

        #building dojo with our profile
        profnode = depnode.find_node(DOJO_PROFILE)
        if profnode is None: conf.fatal("dojo build profile was not found. Please run waf configure.")
        #else: print "profile path " + profnode.abspath()

        #check if dojo was already built
        dojorelnode = dojonode.find_dir('release')
        if dojorelnode is None :
          bsnode = dojonode.find_dir("util/buildscripts") # location of dojo build scripts
        
          #http://livedocs.dojotoolkit.org/build/buildSystem
          if (platform.system() == 'Windows'):
            buildprog = "cmd.exe /c build.bat"
          else:
            buildprog = "sh build.sh"
        
          conf.start_msg("Building " + profnode.relpath() )
          dojo_build_proc = subprocess.Popen(
            shlex.split( buildprog + " -p \"" + profnode.path_from(bsnode) + "\" --bin java --release" ),
            cwd= bsnode.abspath(),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
          )
          out,err = dojo_build_proc.communicate()
          if dojo_build_proc.returncode == 0 :
            conf.to_log(out)
            conf.to_log(err)
            #finding the mandatory dojo layer
            dojorelnode = dojonode.make_node('release')
          	#needed to create folders on windows
            if not os.path.exists(dojorelnode.abspath()) :
            	dojorelnode.mkdir()
            dojobuildnode = dojorelnode.make_node("dojo_build")
            if not os.path.exists(dojobuildnode.abspath()) :
            	dojobuildnode.mkdir()
            conf.end_msg( dojorelnode.relpath(),"GREEN")
          else :
            conf.end_msg("failed","RED")
            conf.fatal("Command Output : \n" + out + "Error :\n" + err)

        #finding dojo mandatory layer and copying only what we need
        
        dojobuildnode = dojorelnode.find_dir("dojo_build")
        if dojobuildnode is None : conf.fatal("dojo_build was not found in build directory. Cannot continue. TIP: look if java is installed and in the path.")
        dojobaselayer = dojobuildnode.find_node("dojo/dojo.js")
        if dojobaselayer is None : conf.fatal("dojo/dojo.js mandatory base layer was not found in build directory. Cannot continue. TIP: look if java is installed and in the path.")
        dojobaselayer_uc = dojobuildnode.find_node("dojo/dojo.js.uncompressed.js")
        if dojobaselayer_uc is None : conf.fatal("dojo/dojo.js.uncompressed.js base layer was not found in build directory. Cannot continue.")
#        dojoxmobilethemechooser = dojobuildnode.find_node("dojox/mobile/deviceTheme.js")
#        if dojoxmobilethemechooser is None : conf.fatal("dojox/mobile/deviceTheme.js mandatory base layer was not found in build directory. Cannot continue.")
                
        #copying mandatory dojo layer
        conf.start_msg("Extracting Dojo built layer" )
        # creating dojo folder
        scriptdojonode = scriptsnode.make_node(os.path.dirname(dojobaselayer.path_from(dojobuildnode)))
        if not os.path.exists(scriptdojonode.abspath()) :
          scriptdojonode.mkdir()
        shutil.copy(dojobaselayer.abspath(),scriptsnode.make_node(dojobaselayer.path_from(dojobuildnode)).abspath())
        conf.end_msg( scriptsnode.find_node(dojobaselayer.path_from(dojobuildnode)).relpath())
        conf.start_msg("Extracting Dojo built layer - uncompressed" )
        shutil.copy(dojobaselayer_uc.abspath(),scriptsnode.make_node(dojobaselayer_uc.path_from(dojobuildnode)).abspath())
        conf.end_msg( scriptsnode.find_node(dojobaselayer_uc.path_from(dojobuildnode)).relpath())
        
#        #extracting dojox mobile themes
#        conf.start_msg("Extracting Dojox mobile Theme chooser" )
#        # creating dojox folder
#        htdocsdojoxnode = htdocsnode.make_node(os.path.dirname(dojoxmobilethemechooser.path_from(dojobuildnode)))
#        if not os.path.exists(htdocsdojoxnode.abspath()) :
#          htdocsdojoxnode.mkdir()
#        shutil.copy(dojoxmobilethemechooser.abspath(),htdocsnode.make_node(dojoxmobilethemechooser.path_from(dojobuildnode)).abspath())
#        conf.end_msg( htdocsnode.find_node(dojoxmobilethemechooser.path_from(dojobuildnode)).relpath())
        
        conf.start_msg( "Extracting Dojox Mobile Themes ")
        dmblthemes_build = dojobuildnode.find_node("dojox/mobile/themes")
        if dmblthemes_build is None : conf.fatal("dojox/mobile/themes for dojox mobile themes was not found in build directory. Cannot continue.")        
        dmbltnode = htdocsnode.make_node("dojox/mobile/themes")
        if os.path.exists(dmbltnode.abspath()) : #remove existing dojox dir
          shutil.rmtree(dmbltnode.abspath(), 1)
          if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
        dmbltnode.mkdir()
        for ftname in ['android','blackberry','common','custom','iphone']:          
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
                    if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
                  shutil.copytree (thimg.abspath(), thimagesnode.abspath() )
                  
                #ipad specific from iphone theme
                ipadcss = thdir.find_node("ipad.css")
                if ipadcss is not None :
                  shutil.copy( ipadcss.abspath(), thnode.abspath())
          
        conf.end_msg( "ok" )

        # Copying doh for testing purposes into our tests directory
        testsnode =  conf.path.find_dir('tests')
        #if testsnode is None : conf.fatal("tests/ subfolder was not found. Cannot continue.")
        
        if testsnode is not None :
          dohnode = dojonode.find_dir('util/doh')
          if dohnode is None : conf.fatal("util/doh subfolder was not found in dojo directory. Cannot continue.")
  
          dohdstnode = testsnode.make_node('doh')
          conf.start_msg( "Copying " + dohnode.relpath() + " to " + dohdstnode.relpath() )
          if os.path.exists(dohdstnode.relpath()) :
            shutil.rmtree(dohdstnode.relpath())
            if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
          shutil.copytree(dohnode.relpath(), dohdstnode.relpath())
          conf.end_msg( "ok" )

    else: # no need of dojo
      pass
  
    if conf.env.PLATFORM == 'android' :
        #preparing cordova project
        conf.start_msg("Checking Cordova Project")
        cordova_create_node = conf.path.find_node(conf.env.CORDOVA_PATH).find_node("bin").find_node("create")
        if cordova_create_node is None : conf.fatal("bin/create was not found in " + conf.env.CORDOVA_PATH + ". Cannot continue.")
        
        android_pub_node = conf.path.find_node("publish").find_node("android")
        android_proj_node = android_pub_node.find_node(ANDROID_PROJECT);
        if android_pub_node is None : conf.fatal("Cannot find publish/android path")
        if android_proj_node is None :
            conf.end_msg("failed","RED")
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
        if assetswww_dir is None : bld.fatal("assets/www subfolder was not found. Cannot continue.")
        #cleaning basic cordova project
        for todel in ['css','img','js','res','spec','index.html','main.js','spec.html']:
          delnode = assetswww_dir.find_node(todel)
          if delnode is not None :
              if os.path.isdir(delnode.relpath()) : 
                  shutil.rmtree(delnode.relpath(),True)
                  if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
              elif os.path.isfile(delnode.relpath()) :
                  os.remove(delnode.relpath())
  
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

    #define a portable copy task
    def cp_task(task):
      src = task.inputs[0].abspath()
      tg = task.outputs[0].abspath()
      if os.path.isdir(src) : return shutil.copytree(src,tg)
      elif os.path.isfile(src) : return shutil.copy(src,tg)

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
  
    if bld.env.ENGINE == "dojo" : #dojo and web js engine -> just copy files around

        #define how to copy dojo components. source and target needs to be in the dojolayer. everything else is relative to it
        def cp_dojo_task(task):
	        srcnode = task.inputs[0].parent # get used dojo components from src
	        tgnode = task.outputs[0].parent # prepare to copy them to tg
	        
	        #copy required resources
	        for dcmpnt in ['dojo.js','../app/nls', 'resources','css','dijit'] : #build : copying the result of config into build folder
	        	dcnode = srcnode.get_src().find_node(dcmpnt)
	        	if dcnode is None : bld.fatal(os.path.join(srcnode.get_src().relpath(),dcmpnt) + " not found. Aborting.")
	        	if os.path.isdir(dcnode.abspath()) :
	        		bld_dcnode = tgnode.make_node(dcnode.path_from(srcnode))
	        		if os.path.exists(bld_dcnode.abspath()) :
	        		    shutil.rmtree(bld_dcnode.abspath())
	        		    if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
	        		res = shutil.copytree(dcnode.get_src().abspath(),bld_dcnode.abspath())
	        	else :
	        		srccp = dcnode.get_src().abspath();
	        		tgtcp = tgnode.make_node(dcnode.path_from(srcnode)).abspath();
	        		if not os.path.exists(os.path.dirname(tgtcp)) :
	        			os.makedirs(os.path.dirname(tgtcp))
	        		res = shutil.copy(srccp,tgtcp)
	        return res

        #find htdocs dir
        htdocs_dir = bld.path.get_src().find_dir('htdocs')
        if htdocs_dir is None : bld.fatal("htdocs/ subfolder was not found. Cannot continue.")
        #find scripts dir
        scripts_dir = htdocs_dir.find_dir('scripts')
        if scripts_dir is None : bld.fatal("htdocs/scripts subfolder was not found. Cannot continue.")
        #find app dir
        app_dir = scripts_dir.find_dir('app')
        if app_dir is None : bld.fatal("htdocs/scripts/app subfolder was not found. Cannot continue.")
        	
        #create dirs 
        for folder in ['scripts/app']:
          foldernode = bldnode.make_node(folder)
          foldernode.mkdir()         
          if bld.env.PLATFORM == 'android' :
            androidfoldernode = assetswww_dir.make_node(folder)
            androidfoldernode.mkdir() 
        
        #copy content                                          
        for folder in ['audio','content','css','dojox', 'fonts','images']:        	
	        _destDir = os.path.join(bldnode.abspath(), folder)
	        if os.path.exists(_destDir) :
	          shutil.rmtree(_destDir) #remove existing dir 
	          if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
	        shutil.copytree(os.path.join(htdocs_dir.abspath(),folder), _destDir)
	        
	        if bld.env.PLATFORM == 'android' :
	            _android_destDir = os.path.join(assetswww_dir.abspath(), folder)
	            if os.path.exists(_android_destDir) :
	              shutil.rmtree(_android_destDir) #remove existing dir 
	              if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
	            shutil.copytree(_destDir, _android_destDir) #we copy from wbuild

#        # handle images/
#        for img in htdocs_dir.get_src().ant_glob('images/**/*.png images/**/*.gif images/**/*.jpg'): # find images files
#          bld(
#            rule=cp_task,
#            source=img.get_src(),
#            target=bldnode.make_node(img.path_from(htdocs_dir))
#          )# copy them to the build directory
#          if bld.env.PLATFORM == 'android' :
#              #copying
#              bld(
#                rule=cp_task,
#                source=bldnode.make_node(img.path_from(htdocs_dir)), # task implicit dependency
#                target=assetswww_dir.make_node(img.path_from(htdocs_dir))
#              )
#        
#        
#        # handle fonts/
#        for fnt in htdocs_dir.get_src().ant_glob('fonts/*.otf fonts/*.ttf fonts/*.svg fonts/*.eot fonts/*.txt fonts/.htaccess'):      # find font files          
#          bld(
#            rule=cp_task,
#            source=fnt.get_src(),
#            target=bldnode.make_node(fnt.path_from(htdocs_dir))
#          )# copy them to the build directory
#          if bld.env.PLATFORM == 'android' :
#              #copying
#              bld(
#                rule=cp_task,
#                source=bldnode.make_node(fnt.path_from(htdocs_dir)),
#                target=assetswww_dir.make_node(fnt.path_from(htdocs_dir)),
#              )
#        
#        # handle css/ 
#        for css in htdocs_dir.get_src().ant_glob('css/*.css'):      # find css files
#          bld(
#            rule=cp_task,
#            source=css.get_src(),
#            target=bldnode.make_node(css.path_from(htdocs_dir))
#          )# copy them to the build directory
#          if bld.env.PLATFORM == 'android' :
#              #copying
#              bld(
#                rule=cp_task,
#                source=bldnode.make_node(css.path_from(htdocs_dir)),
#                target=assetswww_dir.make_node(css.path_from(htdocs_dir)),
#                always=True
#              )
#        
#        # handle content/ 
#        for graphmls in htdocs_dir.get_src().ant_glob('content/*.graphml'): ### content/.htaccess'):      # find graphml files
#          bld(
#            rule=cp_task,
#            source=graphmls.get_src(),
#            target=bldnode.make_node(graphmls.path_from(htdocs_dir))
#          )# copy them to the build directory
#          #_nc_dir = graphmls.get_src().abspath() # + os.path.splitext(graphmls.get_src())[0]
#          #print _nc_dir
#          head, tail = os.path.split(graphmls.get_src().abspath())
#          _nc_dir = os.path.join(head, os.path.splitext(tail)[0])
#          print _nc_dir
#          bld(
#            rule=cp_task,
#            source=_nc_dir,
#            target=bldnode.make_node(graphmls.path_from(htdocs_dir))
#          )
#          if bld.env.PLATFORM == 'android' :
#              #copying
#              bld(
#                rule=cp_task,
#                source=bldnode.make_node(graphmls.path_from(htdocs_dir)),
#                target=assetswww_dir.make_node(graphmls.path_from(htdocs_dir))
#              )
#        
#        # handle audio/
#        for audio in htdocs_dir.get_src().ant_glob('audio/**/*.ogg audio/**/*.mp3 audio/**/*.wav'): # find audio files
#          bld(
#            rule=cp_task,
#            source=audio.get_src(),
#            target=bldnode.make_node(audio.path_from(htdocs_dir))
#          )# copy them to the build directory
#          if bld.env.PLATFORM == 'android' :
#              #copying
#              bld(
#                rule=cp_task,
#                source=bldnode.make_node(audio.path_from(htdocs_dir)),
#                target=assetswww_dir.make_node(audio.path_from(htdocs_dir))
#              )
#          
#        # copy htdocs/../dojox/mobile/themes/
#        dojox_destDir = os.path.join(bldnode.abspath(), "dojox")
#        if os.path.exists(dojox_destDir) :
#          shutil.rmtree(dojox_destDir) #remove existing dir
#          if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
#        shutil.copytree(os.path.join(htdocs_dir.abspath(),'dojox'), dojox_destDir)
#        #BUG HERE if the dir is present, the removal is not fast enough at least on windows and the waf build command must be run another time ...
#        if bld.env.PLATFORM == 'android' :
#            dojox_android_destDir = os.path.join(assetswww_dir.abspath(), "dojox")
#            if os.path.exists(dojox_android_destDir) :
#              shutil.rmtree(dojox_android_destDir) #remove existing dir
#              if (platform.system() == 'Windows'): time.sleep(WINDOWS_SLEEP_DURATION) #sleep to allow deletion on Windows
#            shutil.copytree(dojox_destDir, dojox_android_destDir)
#        
        
        #html files
        for html in htdocs_dir.get_src().ant_glob('*.html *.txt *.php'):      # find static files
          bld(
            rule=cp_task,
            source=html.get_src(),
            target=bldnode.make_node(html.path_from(htdocs_dir))
          )# copy them to the build directory
          if bld.env.PLATFORM == 'android' :
              #copying
              bld(
                rule=cp_task,
                source=bldnode.make_node(html.path_from(htdocs_dir)),
                target=assetswww_dir.make_node(html.path_from(htdocs_dir))
              )
        
        #dojo        
#        dojo_layer = scripts_dir.get_src().find_node('dojo/dojo.js') # build dojo layer
#        if dojo_layer is None : bld.fatal(os.path.join(scripts_dir.relpath(),"dojo/dojo.js") + " not found")        
#        bld(
#            rule=cp_task,
#            source=dojo_layer.get_src(),
#            target=bldnode.make_node(dojo_layer.path_from(htdocs_dir))
#        )# copy dojo to the build directory
#        if bld.env.PLATFORM == 'android' :
#          #copying
#          bld(
#            rule=cp_task,
#            source=bldnode.make_node(dojo_layer.path_from(htdocs_dir)),
#            target=assetswww_dir.make_node(dojo_layer.path_from(htdocs_dir))
#          )
        #dojo + ressources   ##NB: we should build ressources using dojo !!
        dojo_layer = scripts_dir.get_src().find_node('dojo/dojo.js')	# build dojo layer
        if dojo_layer is None : bld.fatal(os.path.join(scripts_dir.relpath(),'dojo/dojo.js') + " not found")
        bld(
					rule=cp_dojo_task,
					source=dojo_layer.get_src(),
					target=bldnode.make_node(dojo_layer.path_from(htdocs_dir))
        )# copy dojo to the platform build directory
        if bld.env.PLATFORM == 'android' :
          #copying
          bld(
            rule=cp_dojo_task,
					  source=dojo_layer.get_src(),
					  target=assetswww_dir.make_node(dojo_layer.path_from(htdocs_dir))
          )
        
        #markdown.js
        markdown = scripts_dir.get_src().find_node('Markdown.Converter.js')
        bld(
            rule = cbuild_task,
            source = markdown.get_src(),
            target = bldnode.make_node(markdown.path_from(htdocs_dir))
        )
        #cbuild_task(markdown.get_src().abspath(), bldnode.make_node(markdown.path_from(htdocs_dir)).abspath(), False)
        if bld.env.PLATFORM == 'android' :
            bld(
                rule = cbuild_task,
                source = bldnode.make_node(markdown.path_from(htdocs_dir)),
                target = assetswww_dir.make_node(markdown.path_from(htdocs_dir))
            )
            #cbuild_task(bldnode.make_node(markdown.path_from(htdocs_dir)).abspath(), assetswww_dir.make_node(markdown.path_from(htdocs_dir)).abspath(),False)
                    
        #Compile app src files
        for js in app_dir.get_src().ant_glob('*.js'):
          bld(
            rule = cbuild_task,
            source = js.get_src(),
            target = bldnode.make_node(js.path_from(htdocs_dir))
          )
          #cbuild_task(js.get_src().abspath(), bldnode.make_node(js.path_from(htdocs_dir)).abspath() ) # advanced compilation doesn't work right now, find a way to fix that if needed
          if bld.env.PLATFORM == 'android' :
              bld(
                rule = cbuild_task,
                source = bldnode.make_node(js.path_from(htdocs_dir)),
                target = assetswww_dir.make_node(js.path_from(htdocs_dir))
              )
              #cbuild_task(bldnode.make_node(js.path_from(htdocs_dir)).abspath(),assetswww_dir.make_node(js.path_from(htdocs_dir)).abspath() ) # advanced compilation doesn't work right now, find a way to fix that if needed
          
          
          
        #Compile src files into one single file #waf script does work but not final file app.js
#        srcs = ""
#        for js in app_dir.get_src().ant_glob('*.js'):     # find source files
#          srcs = " --js \"" + js.abspath() + "\"" + srcs
#        
#        dest = bldnode.make_node(app_dir.get_src().find_node('app.js').path_from(htdocs_dir)).abspath()
#        cbuild_proc = subprocess.Popen(shlex.split("java -jar \"" + bld.env.COMPILER_PATH + "\" --compilation_level ADVANCED_OPTIMIZATIONS" + srcs + " --js_output_file \"" + dest + "\" --warning_level DEFAULT"), cwd=bld.path.get_src().abspath(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
#        out,err = cbuild_proc.communicate()
#
#        if ( cbuild_proc.returncode != 0 ) :
#          bld.fatal("Closure Compiler failed. Return Code: " + cbuild_proc.returncode + " Error : \n" + err )
#        else :
#          if out is not None and out.strip() != "" :
#            print out
#          if err is not None and err.strip() != "" :
#            print err         
        
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
          #TODO : pass this as param of the task
          debug = True
          dgbopt = " --release "
          if debug is True:
            dbgopt = " --debug "
          
          #finding relevant build script
          buildandroid_node = None
          if os.name == 'posix' and platform.system() == 'Linux':
              buildandroid_node=android_proj_node.find_node("cordova").find_node("build")
              if  buildandroid_node is None : conf.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/build not found.")
              os.chmod(buildandroid_node.abspath(),stat.S_IXUSR | stat.S_IRUSR)	
          elif os.name == 'nt' and platform.system() == 'Windows' :
              buildandroid_node=android_proj_node.find_node("cordova").find_node("build.bat")
              if  buildandroid_node is None : conf.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/build.bat not found.")
            
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
            target = android_proj_node.make_node(os.path.join("bin",ANDROID_PROJECT + "-debug.apk" )),
            always = True
        )
        #androbuild_task(android_proj_node, debug = True)

    elif bld.env.PLATFORM == 'chrome' : 
        ###Creating manifest needed for chrome
        chronode = bld.path.get_src().find_dir("publish/chrome_store") # find chrome_store folder
        if chronode is None : # TODO : setup basic chrome_store structure
          bld.fatal("chrome_store not found")
        def mnfst_version_change(task):
          src = task.inputs[0]
          tg = task.outputs[0].abspath()
          #get bzr rev info
          bzr_rev_proc = subprocess.Popen(shlex.split("bzr revno"),cwd=bld.path.get_src().abspath(),stdout=subprocess.PIPE,stderr=subprocess.PIPE)
          out,err = bzr_rev_proc.communicate()
          if bzr_rev_proc.returncode != 0 : bld.fatal("Cannot determine current bzr revno to set version.")
          else :
            mnfst_str_tmpl = Template(src.read()) # template to do $var based substitution , not to get mixed with json syntax
            mnfst_str = mnfst_str_tmpl.substitute(bzr_rev=out.strip())
          #TODO: probably simpler to use json parser if possible
          #mnfst = json.load(src)
          #TODO : handl errors here
          mnfst_bld_file = open(tg,'w')
          mnfst_bld_file.write(mnfst_str)
          mnfst_bld_file.close()
          return 0
        #looking fo manifest.json
        mnfstnode = chronode.find_node("manifest.json")
        if mnfstnode is None : bld.fatal("manifest.json not found")
        else :
          bld(  rule=mnfst_version_change,
            source = mnfstnode,
            target = bldnode.make_node(mnfstnode.path_from(chronode))
          )
          
        #TODO copy "publish/chrome_store/_locales too
        #TODO copy icons too
        #TODO chrome specifics scripts too

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
        if runandroid_node is None : conf.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/run not found.")
        os.chmod(runandroid_node.abspath(),stat.S_IXUSR | stat.S_IRUSR)	
    elif os.name == 'nt' and platform.system() == 'Windows' :
        runandroid_node=android_proj_node.find_node("cordova").find_node("run.bat")
        if  runandroid_node is None : conf.fatal("ERROR : " + android_proj_node.relpath() + "/cordova/run.bat not found.")
            
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

