{
/*
 Name:
    load_subtitles
 Version:
    1.0 (08 April 2016)
 Author:
    Arnaud Trouve (GingaLab)
    based on http://www.motionscript.com/ae-scripting/create-text-layers-from-file.html
 Description:  
    Prompts the user for a subtitle file (plain text)
    and uses it to create text layers in a new composition.
 Usage:
    copy in C:\Program Files\Adobe\Adobe After Effects CC\Support Files\Scripts
    then in AE: File > Scripts...
*/

	
	function LoadSubtitles()
	{
		var scriptName = "Change Render Locations";
		var theFile = File.openDialog("Select a subtitle file...");
		
		if (theFile != null) {
			app.beginUndoGroup(scriptName);
			
                var fileOK = theFile.open("r");
                if (fileOK){
                   
                    // create project if necessary
                      var proj = app.project;
                      if(!proj) proj = app.newProject();

                      // create new comp named 'my text comp'

                      var compW = 1280; // comp width
                      var compH = 720; // comp height
                      var compL = 15;  // comp length (seconds)
                      var compRate = 24; // comp frame rate
                      var compBG = [48/255,63/255,84/255] // comp background color
                  
                      var myItemCollection = app.project.items;
                      var myComp = myItemCollection.addComp('my subtitle comp',compW,compH,1,compL,compRate);
                      //myComp.bgColor = compBG;

                      // read text lines and create text layer for each
                      // until end-of-file is reached
                      var text;
                      while (!theFile.eof){
                        text = theFile.readln();
                        if (text == "") text = "\r" ;
                        else { 
                                myComp.layers.addText(text);
                            }
                      }

                       // center all layers
                       myComp.layer(1).property("Position").setValue(

                      // close the file before exiting

                      theFile.close();
                }
			
			app.endUndoGroup();
		}
	}
	
	
	LoadSubtitles();
}
