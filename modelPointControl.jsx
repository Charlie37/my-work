/* 
 Name:
    ModelPointControl
 Version:
	1.0 (03 October 2013)
 Author:
    Arnaud Trouvé (AMFX)
    based in part on other works by CR Green, Dan Ebberts, Alejandro Perez, Juan Corcoles
    Thanks to them, and as always, thanks to creativecow.net and aenhancers.com. crgreen.com
 Description:  
    Vertex Linker: animates individual mask vertices by linking them to other (point) properties.
    Note: This is meant to work with a mask layer of the same size of the comp, 
    and that layer should have its default geometric values (size [scale], rotation, position, etc.).
    The 'vertex guide' layer will be (noticably) off if these values have been changed.
 Usage:
    Select a mask and a property
    Click "Create Guide"
    Move the guide layer with the "<" and ">" buttons
    (optional) Activate the padding to add keys every X frames
    Click "Execute"
*/


// This class represents the main class of the script
function VertexLinker()
{
	// Variable used to keep track of 'this' reference
	var vertexLinker = this;
	
	// Create an instance of the utils class to use its functions
	var utils = new VertexLinkerUtils();

	// Script infos
	this.scriptMinSupportVersion = "9.0";
	this.scriptName = "ModelPointControl.jsx";	
	this.scriptVersion = "1.0";
	this.scriptTitle = "ModelPointControl";
	this.scriptCopyright = "Copyright (c) 2013 Arnaud Trouvé (AMFX)";
	this.scriptDescription = {en:"Animates individual mask vertices by linking them to other (point) properties.", 
							  fr:"Contrôleur Indépendant de Points de Masque: ce script anime des vertices d\\\'un masque en liant le point sélectionné à une autre propriété."};
    this.scriptAbout = {en:this.scriptName + ", v" + this.scriptVersion + "\\r" +  this.scriptCopyright + "\\r\\r" + utils.loc(this.scriptDescription),
						fr:this.scriptName + ", v" + this.scriptVersion + "\\r" +  this.scriptCopyright + "\\r\\r" + utils.loc(this.scriptDescription) };		
	this.scriptUsage = {en:	"\u25BA In After Effects CS4 or later, run the script \\r" +
                                "\u25BA Select a mask and a property \\r" +
							"\u25BA Click on Create Guide \\r" +
							"\u25BA Move the guide layer with the \"<\" and \">\" buttons \\r" + 
							"\u25BA (optional) Activate a padding to add keys to bake animation \\r" +  
							"\u25BA Click on Execute",
						fr:	"\u25BA Dans After Effects CS4 ou supérieur, exécuter le script \\r" +
                                "\u25BA Sélectionner un masque et une propriété \\r" +
							"\u25BA Cliquer sur Créer Guide \\r" +
							"\u25BA Déplacer le guide avec les boutons \"<\" et \">\"  \\r" +
							"\u25BA (optionnel) Définir un intervalle pour la création des images-clés \\r" +
							"\u25BA Cliquer sur Exécuter"};
								
	// Errors
	this.requirementErr = {en:"This script requires After Effects CS4 or later.", fr:"Ce script nécessite After Effects CS4 ou supérieur."};	
	this.noCompErr = {en:"A comp must be active.", fr:"Une composition doit être active."};
	this.noLayersErr = {en:"Select at least one layer.", fr:"Sélectionnez au moins un calque."};

	// UI strings & default values 
	this.aboutBtnName = "?";
	this.secondsCbName = {en:"Seconds:", fr:"Secondes:"};
	this.secondsEtDflt = 0;
	this.framesCbName = {en:"Frames:", fr:"Images:"};	 
	this.framesEtDflt = 0;
    this.mkGuideBtnName = {en:"Create Guide", fr:"Créer Guide"};
    this.prevVertexBtnName = {en:"< Prev. Vertex", fr:"< Vertex Préc."};
    this.nextVertexBtnName = {en:"Next Vertex >", fr:"Vertex Suiv. >"};
    this.paddingCbName = {en:"Padding: (min: 0 max: 1)", fr:"Intervalle: (min: 0 max: 1)"};
    this.paddingEtDflt = 0.1;
    this.runBtnName = {en:"Execute", fr:"Exécuter"};
	
    this.preCheckOK = false;
    this.theComp = null;
    this.guideName = "vertex guide";
    this.seMaskLayer = null;
    this.theMask = null;
    this.otherProp = null;
    this.workingVertexIndex = 0;
    this.vGuide = undefined;
    this.aiPixelAR = 1;
    this.sePropLayer = null;
    this.pal = null;

    // icons
    this.MPCIconFile = new File("./ModelPointControl/MPC.png");
    
	// Creates and displays the script interface
	this.buildUI = function (thisObj)
	{
		// dockable panel or palette
        this.pal = (thisObj instanceof Panel) ? thisObj : new Window("palette", this.scriptTitle, undefined, {resizeable:false});

		// resource specifications
		var res =
		"group { orientation:'column', alignment:['left','top'], alignChildren:['right','top'], \
            gr6: Group { \
                mkGuideBtn: Button { text:'" + utils.loc(this.mkGuideBtnName) + "', preferredSize:[100,20] }, \
                prevVertexBtn: Button { text:'" + utils.loc(this.prevVertexBtnName) + "', preferredSize:[100,20] }, \
                nextVertexBtn: Button { text:'" + utils.loc(this.nextVertexBtnName) + "', preferredSize:[100,20] } \
            }, \
            gr5: Group { \
                paddingCb: Checkbox { text:'" + utils.loc(this.paddingCbName) + "', value:true }, \
                paddingEt: EditText { text:'" + this.paddingEtDflt + "', characters:5 } \
            }, \
            gr4: Group { \
                runBtn: Button { text:'" + utils.loc(this.runBtnName) + "' } \
            } \
		}";
        
        var res2 =
		"group { orientation:'column', alignment:['left','top'], alignChildren:['right','top'], \
			gr2: Group { \
                    logSt: StaticText { preferredSize:[133,32], text:'', multiline:true } \
                    iconBtn: IconButton { preferredSize:[133,32], helpTip:'" + utils.loc(this.mkGuideBtnName) + "' }, \
                    aboutBtn: Button { text:'" + this.aboutBtnName + "', preferredSize:[25,20] } \
			} \
		}"; 

        this.pal.gr2 = this.pal.add(res2);
        this.pal.progArea = this.pal.add("statictext", [-50,0,266,54], 'Click \"Create Guide\" first,\nthen move the guide layer with the \"<\" and \">\" buttons.', {multiline:true} );
        this.pal.gr = this.pal.add(res);

        // GUI
        this.pal.gr2.gr2.iconBtn.icon = this.MPCIconFile;
        
        // event callbacks
        this.pal.gr2.gr2.aboutBtn.onClick = function () 
        { 
            utils.createAboutDlg(vertexLinker.scriptAbout, vertexLinker.scriptUsage); 
        };

        this.pal.gr.gr5.paddingCb.onClick = function () 
        { 
            if ( this.pal.gr.gr5.paddingEt.visible )
                this.pal.gr.gr5.paddingEt.visible = false;
            else
                this.pal.gr.gr5.paddingEt.visible = true;
        };
		
		this.pal.gr.gr4.runBtn.onClick = function () 
		{ 
            vertexLinker.linkClick();
		};
    
        this.pal.gr.gr6.mkGuideBtn.onClick = function ()
        {
            vertexLinker.newGuideClick();
        };
    
        this.pal.gr.gr6.prevVertexBtn.onClick = function ()
        {
            vertexLinker.moveGuideBackClick();
        };
    
        this.pal.gr.gr6.nextVertexBtn.onClick = function ()
        {
            vertexLinker.moveGuideClick();
        };
		
		// show user interface
		if (this.pal instanceof Window)
		{
			this.pal.center();
			this.pal.show();
		}
		else
		{
			this.pal.layout.layout(true);
		}	   
	};

	// Determines whether the active item is a composition  
	this.checkActiveItem = function () 
	{
		return !(app.project.activeItem instanceof CompItem);
	};

	// Checks if initial requirements are met  
    this.mainPreCheck = function ()
    {
        this.preCheckOK = false;

        if (app.project != null)
        {
            if (app.project.activeItem != null)
            {
                if (app.project.activeItem instanceof CompItem)
                {
                    var propSel = app.project.activeItem.selectedProperties;
                    var selLength = propSel.length;

                    if (selLength < 2)
                    {//might want to add || selLength > 2
                        alert("Please select one mask and one other property.");
                    }
                    else
                    {
                        this.theComp = app.project.activeItem;

                        for (var thisSelectedProp = 0; thisSelectedProp <= selLength; thisSelectedProp++)
                        {
                            if (propSel[thisSelectedProp].matchName == "ADBE Mask Atom")
                            {
                                this.theMask = propSel[thisSelectedProp];// grab first mask encountered
                                //get its layer (um ... is this the easiest/most efficient way? i was hoping something like property.layer would work)
                                deepness=propSel[thisSelectedProp].propertyDepth;
                                d = propSel[thisSelectedProp];
                                for (var i=1;i<=deepness;i++)
                                {
                                    d=d.parentProperty;
                                }
                            
                                this.seMaskLayer = d;
                                break;
                            }
                        }

                        /////////////////
                        if ( this.theMask != null )
                        {
                            for (var selPropIndex = 0; selPropIndex <= selLength; selPropIndex++)
                            {
                                thisProp = propSel[selPropIndex];                                
                                if (thisProp != undefined && thisProp.constructor.name == "Property")
                                {
                                    // okay, it's a property, now look for a 2D array (might want to include numbers and 3D arrays if this fails ... )
                                    if (thisProp.value.constructor == Array)
                                    {
                                        // it's an array, now how many dimensions?
                                        propDim = thisProp.value.length;
                                        if (propDim >1) 
                                        { //for now, we'll just accept 2 or greater D properties
                                            //now, make sure these are numbers:
                                            if ( (thisProp.value[0].constructor == Number) && (thisProp.value[1].constructor == Number) )
                                            {
                                                this.otherProp = thisProp;
                                                //get its layer
                                                deepness=thisProp.propertyDepth;
                                                d = thisProp;
                                                for (var i=1;i<=deepness;i++)
                                                {
                                                    d=d.parentProperty;
                                                }
                                                this.sePropLayer = d;

                                                break;
                                            }
                                        }
                                    }
                                }
                            }
                        
                            if ( this.otherProp != null )
                            {
                                this.preCheckOK = true; // huzzah!
                            }
                            else
                            {
                                alert("No appropriate property selected.");
                            }
                        }
                        else
                        {
                            alert("No mask selected.");
                        }
                    }// if (app.project.activeItem.selectedProperties.length != 2)
                }
            }
        }
    }

    //  Creates a new guide or enables existing one
    this.newGuideClick = function ()
    {
        this.mainPreCheck();
        
        if (this.preCheckOK)
        {
            if ( this.theComp.layer(this.guideName) == undefined )
            {
                app.beginUndoGroup("Vertex Guide Creation");
                this.makeNewVGuide();
                app.endUndoGroup();
            }
            else
            {
                if ( ! this.theComp.layer(this.guideName).enabled )
                {
                    this.theComp.layer(this.guideName).enabled = true;
                }
            }
        }
    };

    this.makeNewVGuide = function ()
    {
        var guideColor = [255, 255, 0];
        var crossHairVertsHoriz = [ [0,49],[0,52],[101,52],[101,49] ];
        var crossHairVertsVerti = [ [52,0],[49,0],[49,101],[52,101] ];
        var guideSize = 101;
        // Creates a solid
        this.vGuide = this.theComp.layers.addSolid(guideColor, this.guideName, guideSize, guideSize, this.aiPixelAR);
        // Makes it a guide layer
        this.vGuide.guideLayer = true;
        this.putMaskInLayer(this.vGuide, crossHairVertsHoriz, MaskMode.DIFFERENCE);
        this.putMaskInLayer(this.vGuide, crossHairVertsVerti, MaskMode.DIFFERENCE);
        this.moveGuideToV();
        ///////////////// in ae7, the selection gets killed when creating the vertex guide, so we deselect guide and reselect mask and point:
        this.vGuide.selected = false;
        this.theMask.selected = true;
        this.otherProp.selected = true;
        ///////////////// 
        this.pal.progArea.text = "\"" + this.otherProp.name + "\" of layer \"" + this.sePropLayer.name +
            "\"\n" + "Mask \"" + this.theMask.name + "\" of layer \"" + this.seMaskLayer.name + "\"";
    }

    this.putMaskInLayer = function (theLayer, theVerts, mMode)
    {
        var crossHair = theLayer.mask.addProperty("ADBE Mask Atom");
        var theShape = new Shape();
        theShape.vertices = theVerts;
        crossHair.maskShape.setValue(theShape);
        crossHair.maskMode = mMode;
    }

    this.moveGuideToV = function ()
    {
        if ( ! this.theComp.layer(this.guideName).enabled) { this.theComp.layer(this.guideName).enabled = true; }

        var myProperty = this.theMask.property("ADBE Mask Shape");
        var myShape = myProperty.value;
        var vertexLimit = myShape.vertices.length;

        if ( this.workingVertexIndex == 0)
        {
            this.workingVertexIndex = vertexLimit;
        }
        this.workingVertexIndex--;
        
        v = myShape.vertices[this.workingVertexIndex];
        this.theComp.layer(this.guideName).Position.setValue(v);

        this.pal.progArea.text = "\"" + this.otherProp.name + "\" of layer \"" + this.sePropLayer.name +
        "\"\n" + "Mask \"" + this.theMask.name + "\" of layer \"" + this.seMaskLayer.name + "\"\nvertex " + this.workingVertexIndex;
    }

    this.moveGuideToVBack = function ()
    {
        if ( ! this.theComp.layer(this.guideName).enabled ) { this.theComp.layer(this.guideName).enabled = true; }

        var myProperty = this.theMask.property("ADBE Mask Shape");
        var myShape = myProperty.value;
        var vertexLimit = (myShape.vertices.length - 1);

        if ( this.workingVertexIndex == vertexLimit)
        {
            this.workingVertexIndex = -1;
        }
        this.workingVertexIndex++;
        
        v = myShape.vertices[this.workingVertexIndex];
        this.theComp.layer(this.guideName).Position.setValue(v);

        this.pal.progArea.text = "\"" + this.otherProp.name + "\" of layer \"" + this.sePropLayer.name +
        "\"\n" + "Mask \"" + this.theMask.name + "\" of layer \"" + this.seMaskLayer.name + "\"\nvertex " + this.workingVertexIndex;
    }

    this.moveGuideClick = function ()
    {
        this.mainPreCheck();
        if ( this.preCheckOK )
        {
            if ( this.theComp.layer(this.guideName) != undefined)
            {
                this.moveGuideToV();
            }
        }
    }

    this.moveGuideBackClick = function ()
    {
        this.mainPreCheck();
        if ( this.preCheckOK )
        {
            if ( this.theComp.layer(this.guideName) != undefined )
            {
                this.moveGuideToVBack();
            }
        }
    }

    // Applies creation of keys
    this.linkClick = function ()
    {                       
        this.mainPreCheck();
        if (this.preCheckOK)
        {    
            if (this.theComp.layer(this.guideName) != undefined)
            {
                app.beginUndoGroup("Link Vertex to Point");
                this.linkVertexToProp(this.pal);
                app.endUndoGroup();
            }
            else
            {
                alert("You have to create a vertex guide layer first.");
            }
        }
    };

    // Actually lnks vertexes and creates keys
    this.linkVertexToProp = function(pal)
    {                
        var myIn = this.seMaskLayer.inPoint;
        var myOut = this.seMaskLayer.outPoint;
        var f = Math.round(myIn/this.theComp.frameDuration); // frame counter

        var myProperty = this.theMask.property("ADBE Mask Shape");
        var myShape = myProperty.value;

        var t,p,vv;
        var padding = parseFloat(pal.gr.gr5.paddingEt.text);

        while ( f <= Math.round(myOut/this.theComp.frameDuration) )
        {
            this.pal.progArea.text = "Setting keyframe " + f;
            
            // Applies padding, if selected and correct,
            if ( pal.gr.gr5.paddingCb.value && ! isNaN (padding) && padding >= 0.0 && padding <= 1.0 ) t = f*padding else t = f*this.theComp.frameDuration

            p = this.otherProp.valueAtTime(t,false);
            myShape = myProperty.valueAtTime(t,true);
            vv = myShape.vertices;
            vv[this.workingVertexIndex] = [p[0], p[1]];
            myShape.vertices = vv;
            myProperty.setValueAtTime(t,myShape);
            f++;
        }
    
        // now we get the selection back to where it was
        this.theMask.selected = false;//mask shape gets selected when adding keyframes, so we deselect the whole mask first
        this.theMask.selected = true;//then select just the mask
        this.otherProp.selected = true;
   
        this.pal.progArea.text = "vertex " + this.workingVertexIndex + " of mask \"" + this.theMask.name + "\" of layer \"" + this.seMaskLayer.name
            + "\"\nconnected to " + "\"" + this.otherProp.name + "\" of layer \"" + this.sePropLayer.name + "\".";
    
        if ( this.theComp.layer(this.guideName) != null ) { this.theComp.layer(this.guideName).enabled = false; }
    };

     // Runs the script  
	this.run = function (thisObj) 
	{
		if (parseFloat(app.version) < parseFloat(this.scriptMinSupportVersion))
		{
			utils.throwErr(this.requirementErr);
		}
		else
		{
			this.buildUI(thisObj);
		}	
	};
}

// This class provides some utility functions
function VertexLinkerUtils()
{
	// Variable used to keep track of 'this' reference
	var utils = this;
	
	// String localization function: english and french languages are supported
	this.loc = function (str)
	{
		return app.language == Language.FRENCH ? str.fr : str.en;
	};

	// Displays a window containg a localized error message
	this.throwErr = function (err)
	{
		var wndTitle = $.fileName.substring($.fileName.lastIndexOf("/")+1, $.fileName.lastIndexOf("."));
		Window.alert("Script error:\r" + this.loc(err), wndTitle, true);
	};			

	// Displays a dialog containg the script description and usage
	this.createAboutDlg = function (aboutStr, usageStr)
	{	
        var dlg = new Window("dialog", "About");
	   var res =
		"group { orientation:'column', alignment:['fill','fill'], alignChildren:['fill','fill'], \
			pnl: Panel { type:'tabbedpanel', \
				aboutTab: Panel { type:'tab', text:'Description', \
					aboutEt: EditText { text:'" + this.loc(aboutStr) + "', preferredSize:[360,200], properties:{multiline:true} } \
				}, \
				usageTab: Panel { type:'tab', text:'Usage', \
					usageEt: EditText { text:'" + this.loc(usageStr) + "', preferredSize:[360,200], properties:{multiline:true} } \
				} \
			}, \
			btns: Group { orientation:'row', alignment:['fill','bottom'], \
				okBtn: Button { text:'Ok', alignment:['right','center'] } \
			} \
		}";         
        dlg.gr = dlg.add(res);
        
        dlg.center();
        dlg.show();
	};
}



// Creates an instance of the main class and run it
new VertexLinker().run(this);
