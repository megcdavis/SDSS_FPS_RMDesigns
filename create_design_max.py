"""
Read in fits file containing all four BHM cartons and boss skys/eboss standards
create FPS designs

Pulled from the "Commissioning_example_all_skies.ipynb" within Mugatu
Made by Ilija Medan (thank you Ilija!)
"""

__year__ = "2021-2022"


import sys
sys.path.append("/Users/meg/OneDrive - University of Connecticut/Meg_PhDresearch/scripts_notebooks/FPS/fps_calibrations")
sys.path.append("/Users/meg/OneDrive - University of Connecticut/Meg_PhDresearch/scripts_notebooks/FPS/roboscheduler/python")
sys.path.append("/Users/meg/OneDrive - University of Connecticut/Meg_PhDresearch/scripts_notebooks/FPS/robostrategy/python")
from peewee import *
import numpy as np
import robostrategy.field as field
import roboscheduler.cadence as cadence
from coordio.utils import radec2wokxy
import robostrategy.obstime as obstime
import coordio.time
from astropy.table import Table



print("CONNECTING TO UTAH (cadences)")
## server stuff for cadences
from sdssdb.peewee.sdss5db import targetdb

targetdb.database.connect_from_parameters(user='sdss_user', password='4-replicant',
                                         host='localhost',
                                         port=7500)


####SETTINGS BEGIN HERE###


field_designing = "RM"
data_file = r"BHM_cartons_RM_survey_v0.5.fits"
savename = r"BHM_RM_test.fits"

# specify the field center and position angle
#from: https://wiki.sdss.org/display/BHM/Reverberation+Mapping
#XMM LSS
racen = 213.7041666
deccen = 53.075
position_angle=25.5
obsTime = 2459458.5
skies = 50
standards = 70
observatory = 'APO'
cartons_used = ['bhm_rm_known_spec', 'bhm_rm_ancillary', 'bhm_rm_core','bhm_rm_var', 'ops_sky_boss', 'ops_std_eboss']

#IF CANDENCE NEEDS TO BE RESET, MUST RESET AFTER WHERE CADENCES ARE CALLED!!!
#cadence_used = 'dark_174x8'
cadence_used = 'dark_1x1'
print("------------- CURRENT SETTINGS -------------")
#open and line strip param file
#default if no argument given
#STRIP FIELD, OBSERVATORY, RACEN, DECCEN, POSITION ANGLE from fits file in future?

try:
    data_file = sys.argv[1]
    position_angle = float(sys.argv[2])
    racen = float(sys.argv[3])
    deccen = float(sys.argv[4])
    observatory = str(sys.argv[5])
    savename = sys.argv[6]
    print("using file: {}".format(data_file))
except: #IndexError, but might as well catch 'em all!
    print("Using default filename: {}".format(data_file))
    
if observatory == 'APO':
    r_search = 1.49
else:
    r_search = 0.95
    
print("observatory: {}".format(observatory))
print("field creating designs for: {}".format(field_designing))
print("field centers: RA: {} DEC: {}".format(racen, deccen))
print("position angle: {}".format(position_angle))
print("observation mjd: {}".format(obsTime))
print("skies: {} standards: {}".format(skies, standards))
print("cadence set: {}".format(cadence_used))
print("")
print("CARTONS USING: {}".format(cartons_used))
print("--------------------------------------------")

#read in data file
#SAVE COLUMNS TO NUMPY ARRAYS
data = Table.read(data_file, format='fits')
catalogid = np.array(data["catalogid"], dtype=np.int64)
ra = np.array(data["ra"])
dec = np.array(data["dec"])
target_pk = np.array(data["target_pk"], dtype=np.int64)
priority = np.array(data["priority"])
value = np.array(data["value"])
carton = np.array(data["carton"], dtype=str)
instrument = np.array(data["instrument"], dtype='<U10')
carton_to_target_pk = np.array(data["carton_to_target_pk"])
magnitudes = np.zeros((len(data["g"]),10))
magnitudes[:, 0] = data["g"]
magnitudes[:, 1] = data["r"]
magnitudes[:, 2] = data["i"]
magnitudes[:, 3] = data["z"]
magnitudes[:, 4] = data["bp"]
magnitudes[:, 5] = data["gaia_g"]
magnitudes[:, 6] = data["rp"]
magnitudes[:, 7] = data["j"]
magnitudes[:, 8] = data["h"]
magnitudes[:, 9] = data["k"]
program = np.array(data['program'])
category = np.array(data['category'])
tag = np.array(data['tag'])
plan = np.array(data['plan'])


print("COORDIO.")
#coordio stuff
# specify observation time
ot = obstime.ObsTime(observatory=observatory.lower())
obsTime = coordio.time.Time(ot.nominal(lst=racen)).jd

# convert to x,y
x, y, fieldWarn, HA, PA_coordio = radec2wokxy(ra=ra,
                                              dec=dec,
                                              coordEpoch=np.array([2457174] * len(ra)),
                                              waveName=np.array(list(map(lambda x:x.title(), instrument))),
                                              raCen=racen,
                                              decCen=deccen,
                                              obsAngle=position_angle,
                                              obsSite=observatory,
                                              obsTime=obsTime)
# need to load cadences before building designs
print("CADENCE.")
clist = cadence.CadenceList()
clist.fromdb(version='v1')
clist.cadences['dark_1x1'].obsmode_pk = ['dark_rm']

# create the field object
f = field.Field(racen=racen, deccen=deccen, pa=position_angle,
                field_cadence=cadence_used, observatory=observatory.lower(),
                verbose=True)

#f.design_mode = np.array(['dark_rm'])

# set the required skies, in this case all fibers
#zero ap stars and standards

#MEG & JON: CHANGE FOR WHAT WE WANT
f.required_calibrations['sky_boss'] = [skies] #50
f.required_calibrations['standard_boss'] = [standards] #70
f.required_calibrations['sky_apogee'] = [0] #none
f.required_calibrations['standard_apogee'] = [0] #non 

f.achievable_calibrations['sky_boss'] = [skies] #50
f.achievable_calibrations['standard_boss'] = [standards] #70
f.achievable_calibrations['sky_apogee'] = [0] #none
f.achievable_calibrations['standard_apogee'] = [0] #non 

# create array for RS field
N = len(ra)
# these are datatypes from robostrategy.Field
# these are datatypes from robostrategy.Field
targets_dtype = np.dtype([('ra', np.float64),
                          ('dec', np.float64),
                          ('epoch', np.float32),
                          ('pmra', np.float32),
                          ('pmdec', np.float32),
                          ('parallax', np.float32),
                          ('lambda_eff', np.float32),
                          ('delta_ra', np.float64),
                          ('delta_dec', np.float64),
                          ('magnitude', np.float32, 10),
                          ('x', np.float64),
                          ('y', np.float64),
                          ('within', np.int32),
                          ('incadence', np.int32),
                          ('priority', np.int32),
                          ('value', np.float32),
                          ('program', np.unicode_, 30),
                          ('carton', np.unicode_, 50),
                          ('category', np.unicode_, 30),
                          ('cadence', np.unicode_, 30),
                          ('fiberType', np.unicode_, 10),
                          ('catalogid', np.int64),
                          ('carton_to_target_pk', np.int64),
                          ('rsid', np.int64),
                          ('target_pk', np.int64),
                          ('rsassign', np.int32),
                          ('tag', np.unicode_, 10),
                          ('plan',np.unicode_,10)])


# create an empty array
targs = np.zeros(N, dtype=targets_dtype)

# fill in the relevant columns
targs['ra'] = ra
targs['dec'] = dec
targs['epoch'] = np.zeros(N, dtype=np.float32) + 2015.5
targs['x'] = x
targs['y'] = y
targs['within'] = np.zeros(N, dtype=np.int32) + 1
targs['incadence'] = np.zeros(N, dtype=np.int32) + 1
targs['priority'] = priority
targs['value'] = value
targs['program'] = program
targs['carton'] = carton
targs['category'] = category
targs['cadence'] = np.array([cadence_used] * N, dtype='<U30')
targs['fiberType'] = instrument
targs['lambda_eff'] = np.zeros(N, dtype=np.float32)
targs['lambda_eff'][targs['fiberType'] == 'APOGEE'] = 16000.
targs['lambda_eff'][targs['fiberType'] == 'BOSS'] = 5400.
targs['catalogid'] = catalogid
targs['carton_to_target_pk'] = carton_to_target_pk
targs['rsid'] = np.arange(N, dtype=np.int64) + 1
targs['target_pk'] = target_pk
targs['magnitude'] = magnitudes
targs['rsassign'] = np.zeros(N, dtype=np.int32) + 1

# assign targets
f.targets_fromarray(targs)
print("ASSIGN.")

f.assign_science_cp()

print(f.assess())
print(f.validate())
#save design
print("SAVE.")
f.tofits(savename)
print("DESIGN SAVED. RUN COMPLETE.")
