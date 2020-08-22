import cfscrape
import requests
import eyed3
import sys
import logging
from os import listdir
from os import path
from os import mkdir

### Parameters ###
## Destination for download
dest = sys.argv[1]
## URL for 2 week archive, get from wdcb.org/archive network traffic
url = sys.argv[2]
##################

class hh_scraper:
	# Scraper used for all get requests
	scraper = cfscrape.create_scraper()

	# Grabs the list of all free episodes
	# Returns dictionary with key of episode name and value of html element
	def getFreeEpisodeList(url):

	# Finds out which episodes alrady exist in the destination directory
	# Returns dictionary with only episodes that do not already exist
	def getNewEpisodeList(dest):

	# Downloads the album art for each episode from the specified url
	# Returns image path
	def downloadEpisodeImage(imageUrl):

	# Follows the episode url and finds the link to the audio
	# Returns link to audio
	def getEpisodeDownloadUrl(episodeUrl):

	# Downloads and tags audio file
	def downloadEpisodeAudio(url, imagePath, trackNum):

# Checks for a valid internet connection every 'interval' seconds up to a maximum of 'seconds' seconds
def waitForInternetConnection(seconds, interval):
	# Loop until either valid request is made or time is up
	while interval < seconds:
		try:
			r = requests.get('https://www.google.com')
		except:
			sleep(interval)
			interval += interval
			continue

		# If a ok status is returned, then there is a valid internet connection
		if r.status_code == requests.codes.ok:
			return True

	return False

# Set up logging file if not exists
logging_path = path.dirname(path.abspath(__file__)) + '/.logs'
logging_file = logging_path + '/hardcore_history_scraper.log'

if not path.exists(logging_file):
	if not path.exists(logging_path):
		mkdir(logging_path)
	fh = open(logging_file, 'w+')
	fh.close()

# Set up logging
logging.basicConfig(filename=logging_file, filemode='a', format='%(asctime)s %(message)s', level=logging.INFO)

# Check if destination exists
if not path.exists(dest):
	logging.error("Specified destination does not exist. Exiting...")
	sys.exit()

# Create list of currently stored episodes
# Connect to page, collect all new episode titles and links until existing episode is found
# Process each episode, OLDEST FIRST
# Find download link
# Download episode
# Give mp3 tags