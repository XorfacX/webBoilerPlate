webBoilerPlate
===

The project aim is to be the root of all web project.
It contains the structure and scripts design to start a project with a proper configuration.

It uses:
* javascript framework: dojo
* script tool: waf
* build tool: closure compiler
* build script: app.profile.js which must be updated to fit your project


HowTo
---
./waf configure --download --engine=[dojo] --platform=[android|local|chrome|owa|facebook]   
./waf build --partial --bT=[debug|release]   
./waf dist_[chrome]   
./waf distclean


Dependencies
---
Python >2.6 <3 to be able to execute waf script (TODO update to python 3)   
NodeJS for mobile packaging though Apache Cordova
