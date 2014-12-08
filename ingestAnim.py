#!/usr/bin/python

# Ingests .mov file into asset manager.

import sys, os, string, getopt, re, shutil
from optparse import OptionParser

def usage():
	print ("ingestAnim [OPTIONS] [texture_directory]")
	print ("Cut movie animatic for selected reel.\n")
	print ("Options:")
	print ("  -h, --help\t\tShow this help")
	print ("  -f, --farm\tBuild on the renderfarm")
	print ("  -n, --export_name\tAdd a prefix to the filename")
	print ("  -y, --slug_list\tif scene is cut, display shots' slugs")
	print ("  -z, --editin_list\tif scene is cut, display shots' frame counter")

def FormatStr(value, ms) :
	string = str(value)
	length = len(string)
	if ms :
		if length == 1 : string = "00" + string
		elif length == 2 : string = "0" + string
	elif length == 1 : string = "0" + string
	return string

def publish_files(project, user, copyjpeg, tmp_path, filename, part_filename, slug, publish_output = ""):
	# Get environment variables 
	env_div = "###################" + project;
	file_env = open(env_div, "r" )
	assetmg_path = "###################"
	for line in file_env:
		match = re.match(r'(export )(.*)=(.*)', line)
		if (match):
			# print "PUTENV :: " + match.group(2) + " - " + match.group(3)
			os.putenv(match.group(2), match.group(3))
			if match.group(2) == "###################" :
				assetmg_path = match.group(3)
	file_env.close()
	os.putenv("USER", user)

	# Call assetmg to publish
	if copyjpeg:
		published_directory = os.path.dirname(publish_output)
		published_file = (".").join(os.path.basename(publish_output).split(".")[:2])
		command_publish = '%s -f "%s/%s %s %s"' % (assetmg_path, tmp_path, part_filename, published_directory, published_file)
	else: 
		command_publish = assetmg_path + " -p " + tmp_path + "/" + filename + " -c 'animatic for " + slug + "'"
	
	print command_publish

	p = os.popen(command_publish)
	publish_output = p.readline()
	p.close()

	print "output >> " + publish_output

	return publish_output 

def create(args, publish, resultpath, codec, extension, export_name, slug_list, editin_list, idparent, copysound = False, copyjpeg = False):
	user, filepath, editin_str, editlength_str, start_str, project, slug, reel = args
	# codec = "jpeg" if (copyjpeg and copyingjpeg) else codec
	editin = int(editin_str)
	length = int(editlength_str)
	start = int(start_str)

	frameInMs = 41 # number of millisecond in a frame
	#offset	= 96
	offset	= 24
	step	  = 20
	# frame = (editin - 86400) if (reel == "1") else (editin - start) ;
	frame = editin - start;
	hours	 = 0
	mins	  = 0
	secs	  = 0
	ms		= 0

	# TC FOR CUT
	hours = int(frame / (24 * 60 * 60))
	tempA = hours * 24 * 60 * 60
	mins  = int((frame - tempA) / (24 * 60))
	tempB = mins * 24 * 60
	secs  = int((frame - tempA - tempB) / 24)
	restFrame = frame - tempA - tempB - secs * 24
	ms = int(frameInMs * restFrame + offset)
	
	strMs	= FormatStr(ms   , True )
	strSecs  = FormatStr(secs , False) + "."
	strMins  = FormatStr(mins , False) + ":"
	strHours = FormatStr(hours, False) + ":"

	# TC FOR DRAWTEXT
	frame_draw = editin - 86400
	tc_hours = int(frame_draw / (24 * 60 * 60))
	tc_tempA = tc_hours * 24 * 60 * 60
	tc_mins  = int((frame_draw - tc_tempA) / (24 * 60))
	tc_tempB = tc_mins * 24 * 60
	tc_secs  = int((frame_draw - tc_tempA - tc_tempB) / 24)
	tc_restFrame = frame_draw - tc_tempA - tc_tempB - tc_secs * 24

	tcFr	= FormatStr(tc_restFrame   , True )
	tcSecs  = FormatStr(tc_secs , False) + "\:"
	tcMins  = FormatStr(tc_mins , False) + "\:"
	tcHours = FormatStr(tc_hours, False) + "\:"	

	# Create tmp directory if not exists
	tmp_path = "/tmp/cut_videos" if publish else resultpath
	if not os.path.isdir(tmp_path) :
		os.makedirs(tmp_path)

	# Sound info
	# TODO: parameter
	# sound = "mute"
	sound = "scratch voices"
	# sound = "final voices"


	#############################  DRAWTEXT OPTIONS ###########################
	
	fontfile = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
	
	# if scene, display shots' slug + frame counter
	if slug.startswith('sc') and '-sh' not in slug and slug_list and editin_list:

		drawtext = ' -vf "[in]'
		slug_array = slug_list.split(',')
		editin_array = editin_list.split(',')

		if len(slug_array) == len(editin_array):

			# ------------------------ shots' frame counter (begining: frame number) ---------------------------
			drawf = []

			cpte = 0
			for e in editin_array:
				e1 = str(int(editin_array[cpte])-1)

				if cpte+1 < len(editin_array):
					e2 = str(int(editin_array[cpte+1])-1)
				else: # last shot
					e2 = str(length-1)

				cptf = 0
				for x in range(int(e1),int(e2)):
					nbf = int(e1) + int(cptf) + 1

					if cptf < len(drawf):
						drawf[cptf] += 'eq(n,' + str(nbf) + ')+'
					else:
						drawf.append('eq(n,' + str(nbf) + ')+')

					cptf += 1

				cpte += 1

			for idx, val in enumerate(drawf, start=0):
				if val.endswith('+'): val = val[:-1]
				drawtext += 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':draw=\'' + val + '\'' + \
								':text=\'' + str(int(idx)+1) + '\':x=400:y=650, '

			# ------------------------ shots' slug + frame counter (end: frame count) ---------------------------
			cpt = 0
			for s in slug_array:
				e1 = str(int(editin_array[cpt])-1)

				if cpt+1 < len(editin_array):
					e2 = str(int(editin_array[cpt+1])-1)
					length_shot = str(int(e2)-int(e1))

					drawtext += 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':draw=\'if(gt(n,' + e1 + '),lte(n,' + e2 + '))\'' + \
								':text=\'' + project + ' - ' + s + '\':x=50:y=35, '

					drawtext += 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':draw=\'if(gt(n,' + e1 + '),lte(n,' + e2 + '))\'' + \
								':text=\' / ' + length_shot + '\':x=500:y=650, '

				else: # last shot
					drawtext += 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':draw=\'gt(n,' + e1 + ')\'' + \
								':text=\'' + project + ' - ' + s + '\':x=50:y=35, '

					length_shot = str((length-1)-int(e1))
					drawtext += 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':draw=\'gt(n,' + e1 + ')\'' + \
								':text=\' / ' + length_shot + '\':x=500:y=650, '

				cpt+=1

		else: # default
			drawtext += 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=\'' + project + ' - ' + slug + '\':x=50:y=35, '

		# test: custom draw for current frame (because ffmpeg does not allow formatting when n is custom)
		# https://ffmpeg.org/trac/ffmpeg/ticket/1949#comment:16)
		#  error 32512. command line too long ?
		#for z in range(length):
		#	drawtext += 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':draw=\'eq(n,' + str(z) + ')\':text=\'' + str(int(z)+1) + ':expansion=normal:x=800:y=650, '

		# ------------------------ scene's voices + timecode + frame counter ---------------------------
		drawtext +=	'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=\'' + sound + '\':x=850:y=35, ' + \
					'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':timecode=\'' + tcHours + tcMins + tcSecs + tcFr + '\':r=24:x=50:y=650, ' + \
					'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=%{expr\\\\\:n+1} / ' + str(length) + ':expansion=normal:x=850:y=650" '

	else: # shot
		drawtext = ' -vf "[in]drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=\'' + project + ' - ' + slug + '\':x=50:y=35, ' + \
						'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=\'' + sound + '\':x=850:y=35, ' + \
						'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':timecode=\'' + tcHours + tcMins + tcSecs + tcFr + '\':r=24:x=50:y=650, ' + \
						'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=%{expr\\\\\:n+1} / ' + str(length) + ':expansion=normal:x=850:y=650" '
						# 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=%{n} / ' + str(length) + ':expansion=normal:x=1000:y=650" '
						# 'drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':text=\'reel ' + reel + '\':x=1700:y=50" '



	# fontfile = "/usr/share/fonts/truetype/ttf-dejavu/DejaVuSans.ttf"
	# drawtext = ' -vf "[in]drawtext=fontsize=40:fontcolor=White:fontfile=\'' + fontfile + '\':timecode=\'' + tcHours + tcMins + tcSecs + tcFr + '\':r=24:x=50:y=650" '
	

	#############################  FFMPEG VIDEO ###############################

	# Create video file
	ext = extension if (codec != "copy") else filepath.split(".")[1]

	# slug example: sc0560-sh00100 / sc0560
	if not export_name: # part_filename example: sh_sc0560-sh00100_ank.1.animatik / sc_sc0560_ank.1.animatik

		try:
			test = re.search('[sh]+\d{4,5}$', slug).group(0) # is there a shot defined in the slug
			part_filename = project + "_sh_" + slug + "_ank.1.animatik"

		except AttributeError:
			part_filename = project + "_sc_" + slug + "_ank.1.animatik"

	else: # part_filename example: SC0560_SH00100 / SC0560

		try:
			scene = re.search('^[sc]+\d{4}', slug).group(0).upper()

			try:
				shot = re.search('[sh]+\d{4,5}$', slug).group(0).upper()
				part_filename = export_name + "_" + scene + "_" + shot

			except AttributeError:
				part_filename = export_name + "_" + scene

		except AttributeError:
			part_filename = export_name

	filename = part_filename + "." + ext
	command = ""

	if codec == "copy" :
		command = "/systeme/deploy/softs/ffmpeg/ffmpeg -ss " + strHours + strMins + strSecs + strMs + " -i " + filepath + drawtext + " -vframes " + str(length) + \
				  " -qscale 0 -vcodec copy -strict experimental -y " + tmp_path + "/" + filename
	
	if codec == "h264" :
		command = "/systeme/deploy/softs/ffmpeg/ffmpeg -ss " + strHours + strMins + strSecs + strMs + " -i " + filepath + drawtext + " -vframes " + str(length) + \
				  " -qscale 0 -preset medium -vcodec libx264 -pix_fmt yuv420p -strict experimental -y " + tmp_path + "/" + filename

	if codec == "mjpeg" :
		command = "/systeme/deploy/softs/ffmpeg/ffmpeg -ss " + strHours + strMins + strSecs + strMs + " -i " + filepath + drawtext + " -an -vframes " + str(length) + \
				  " -qscale 0 -vcodec mjpeg -strict experimental -y " + tmp_path + "/" + filename

	if command != "":
		print command
		ffmpeg_result = os.system(command)
		print ffmpeg_result

		# 2013-06-21			  
		#if ffmpeg_result != 0:
			# Remove tmp file 
			#shutil.rmtree(tmp_path)
			#sys.exit (1)

		# 2013-07-11
		# list of commands: add shots' frame counter in several steps ??

		#############################  FFMPEG IMAGES ###############################

		if copyjpeg :
			if not os.path.isdir(tmp_path + "/" + part_filename) :
				os.makedirs(tmp_path + "/" + part_filename)
			command_images = "/ffmpeg/ffmpeg -ss " + strHours + strMins + strSecs + strMs + " -i " + filepath + drawtext + " -vframes " + str(length) + \
					  		" -qscale 0 -vcodec mjpeg -strict experimental -y " + tmp_path + "/" + part_filename + "/img_%04d.jpeg"
			print command_images
			ffmpeg_result_images = os.system(command_images)

			if ffmpeg_result_images != 0:
				# remove tmp file (video and images)
				shutil.rmtree(tmp_path)
				sys.exit(1)

		# ####################################  PUBLISH  #######################################

		if publish :
			# publish video
			publish_output = publish_files(project, user, False, tmp_path, filename, part_filename, slug);
			if not publish_output.startswith('/systeme/prod') : # test if file correctly published
				# remove tmp file (video and images)
				# 2013-06-21			  
				#shutil.rmtree(tmp_path)
				sys.exit (1)

			else:
				# if images, publish images
				if (copyjpeg):
					publish_images_output = publish_files(project, user, True, tmp_path, filename, part_filename, slug, publish_output);

		#############################  FFMPEG AUDIO ###############################

		# if copysound :

		# 	audio_filename = part_filename + ".mp3"
		# 	command_audio = "/opt/norman/softs/ffmpeg/ffmpeg  -ss " + strHours + strMins + strSecs + strMs + " -i " + filepath + " -aframes " + str(length) + \
		# 					" -vn -f mp3 -y " + tmp_path + "/" + audio_filename
		# 	print command_audio
		# 	ffmpeg_result_audio = os.system(command_audio)
		# 	if ffmpeg_result_audio != 0:
		# 		sys.exit (1)

		# 	#############################  PUBLISH AUDIO ###############################

		# 	if publish:
				
		# 		command_publish_audio = '%s -f "%s/%s %s %s"' % (assetmg_path, tmp_path, audio_filename, published_directory, published_file + ".wav")
		# 		p = os.popen(command_publish)
		# 		publish_audio_output = p.readline()
		# 		p.close()
		# 		if not publish_audio_output.startswith('/pub') : # test if file correctly published
		# 			sys.exit (1)



###########################################################################################
#                                    MAIN                                                 #
###########################################################################################

try:
	opts, args = getopt.getopt(sys.argv[1:], "fmhpsjr:c:e:n:y:z:i:", ["farm", "master", "help", "publish", "soundcopy", "jpegcopy", "resultpath", "codec", "extension", "export_name", "slug_list", "editin_list", "idparent"])
except getopt.GetoptError, err:
	print str(err)
	usage()
	sys.exit(1)

farm = False
publish = False
master = False
copysound = False
copyjpeg = False
resultpath = ""
codec = "copy"
extension = ""
export_name = ""
slug_list = ""
editin_list = ""
idparent = 0
for o, a in opts:
	if o in ("-h", "--help"):
		usage ()
		sys.exit(2)
	elif o in ("-f", "--farm"):
		farm = True
	elif o in ("-m", "--master"):
		master = True
	elif o in ("-p", "--publish"):
		publish = True
	elif o in ("-s", "--soundcopy"):
		copysound = True
	elif o in ("-j", "--jpegcopy"):
		copyjpeg = True
	elif o in ("-r", "--resultpath"):
		resultpath = a
	elif o in ("-c", "--codec"):
		codec = a
	elif o in ("-e", "--extension"):
		extension = a
	elif o in ("-n", "--export_name"):
		export_name = a
	elif o in ("-y", "--slug_list"):
		slug_list = a
	elif o in ("-z", "--editin_list"):
		editin_list = a
	elif o in ("-i", "--idparent"):
		idparent = a

if not master and len (args) < 8:
	usage()
	sys.exit (1)

if farm:
	if master:
		runonfarm.run ("Cut animatik reel " + args[0], "", "videos")
	else:c
		print "create shot"
		runonfarm.run ("Shot " + args[6], "python ingestAnim.py " + (" ").join(sys.argv[2:]) , str(idparent))

# else:
create(args, publish, resultpath, codec, extension, export_name, slug_list, editin_list, idparent, copysound, copyjpeg)
sys.exit (0)


