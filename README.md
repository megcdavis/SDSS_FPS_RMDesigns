This repository contains the scripts and analysis notebooks for the BHM-RM FPS designs for SDSS-V. 
Authors: Jon Trump and Meg Davis (megan.c.davis@uconn.edu)

Software installation instructions: https://docs.google.com/document/d/1zqhkIVhKqiP1eNojgBWrZDLOZgOEv3t92F1laEY2ofw/edit

As of 10/03/2022, you will need the following versions of the SDSS FPS python packages:
-  Mugatu 1.3.2
-  Roboscheduler 0.11.1
-  Kaiju 1.2.2
-  Coordio 1.4.2
-  Robostrategy 1.4.4
-  fps_calibrations APO.2022.08.31

General script running instructions:
1. ssh to utah (Meg: run ./utah.sh in FPS folder OR run ssh -l USERNAME -L 7500:operations.sdss.org:5432 eboss.sdss.org cat - )
2. edit fps script for defaults, or set up shell script with field carton file, RA, DEC, PA, file save name
3. USE 1x1 CADENCES FOR NOW
4. command-T in terminal for a new window
5. either run the shell script you made or run: time python create_design_max.py
6. ignore warnings for now
7. you'll need to hack the file afterwards, go use the hack_the_fitfiles.ipynb to do so (need to edit the header and change the arrays in hdu 2 to match those of a 174x8 OR 100x8 cadence), contact meg for the examples needed (they are too big to put here).
8. validate locally using the local_validate.ipynb
9. rename and prepare to upload to utah


Uploading designs to Utah:
1. ssh USERNAME@manga.sdss.org
2. cd to the directory Ilija told you to use
3. in local terminal (not ssh'ed into utah): scp /directory/to/designs/* USERNAME@manga.sdss.org:/directory/where/you/want/them/
4. enter password
5. go to the place on utah where you put the designs
6. chmod 670 the files to make them grabbable for everyone else
7. ping Ilija




