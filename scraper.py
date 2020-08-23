import cfscrape
import requests
import eyed3
import sys
import logging
from bs4 import BeautifulSoup
from collections import deque
from os import listdir
from os import path
from os import mkdir

class HHScraper:
	url = None
	dest = None
	scraper = None

	def __init__(self, _url, _dest):
		self._setUpLogging()
		self.url = _url
		self.dest = _dest

		# Initialize Scraper
		self.scraper = cfscrape.create_scraper()
		# Check if destination exists
		if not path.exists(dest):
			logging.error("Specified destination does not exist. Exiting...")
			sys.exit()
		# If destination does not end in /, insert /
		if self.dest[-1] != '/':
			self.dest += '/'

	def scrapeNewEpisodes(self):
		# Get the list of all free episodes available at the moment
		episodeStack = self._getFreeEpisodeList()

		# Get the list of stored episode names
		storedEpisodeList = self._getStoredEpisodeList()

		# Value to calculate track number
		trackAdd = 0
		# Process the list of new episodes
		while len(episodeStack) != 0:
			episode = episodeStack.pop()
			# If the episode is not alread stored, then scrape
			if not episode[0] in storedEpisodeList:
				# Add track to album
				trackAdd += 1
				# Download image and store path
				imagePath = self._downloadEpisodeImage(episode[2])
				# Download and tag episode mp3
				success = self._downloadEpisodeAudio(episode[0], episode[1], episode[2], len(storedEpisodeList) + trackAdd)
				if not success:
					trackAdd -= 1

		logging.info("Scraping complete, " + str(trackAdd) + " new episodes added. Exiting...")


	def _setUpLogging(self):
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

	# Grabs the list of all free episodes
	# Returns stack with key of episode name and list of episode elements
	# [Track Name, Episode URL, Episode Image URL]
	def _getFreeEpisodeList(self):
		logging.info("Gathering Free Episode Information...")
		stack = deque()
		html = self.scraper.get(self.url).text
		soup = BeautifulSoup(html, 'html.parser')

		episodeList = soup.find("div", {"class" : "w-portfolio-list"}).findAll("div", {"class" : "w-portfolio-item hardcore-history-portfolio size_1x1"})
		for episode in episodeList:
			# Get Info about each episode
			title = episode.find("h2").string

			# Normalize URL
			episodeUrl = episode.find("a").get("href")
			if not "dancarlin.com" in episodeUrl:
				episodeUrl = "https://www.dancarlin.com" + episodeUrl

			episodeImageUrl = episode.find("img").get("src")

			# Populate stack
			stack.append([title, episodeUrl, episodeImageUrl])

		return stack

	# Finds out which episodes alrady exist in the destination directory
	# Returns list with only episodes titles that already exist
	def _getStoredEpisodeList(self):
		logging.info("Gathering Stored Episode Information...")
		# Find how many episodes have already been saved
		episodeList = []
		for filename in listdir(dest):
			if "mp3" in filename.split('.')[-1]:
				episodeList.append(filename.split('.mp3')[0])

		return episodeList

	# Downloads the album art for each episode from the specified url
	# Returns image path
	def _downloadEpisodeImage(self, imageUrl):
		# Create hidden image directory if it does not exist
		imageDir = self.dest + ".images"
		if not path.exists(imageDir):
			mkdir(imageDir)

		# Download image
		imagePath = self.dest + ".images/" + imageUrl.split("/")[-1]
		r = self.scraper.get(imageUrl, stream=True)
		if r.status_code == 200:
		    with open(imagePath, 'wb') as f:
		        for chunk in r:
		            f.write(chunk)

		return imagePath

	# Downloads and tags audio file
	# Returns success
	def _downloadEpisodeAudio(self, episodeName, url, imagePath, trackNum):
		logging.info("Downloading Episode: " + episodeName)
		# Go to episode page and find audio url
		html = self.scraper.get(url).text
		soup = BeautifulSoup(html, 'html.parser')

		audioElement = soup.find("audio")
		if audioElement is None:
			logging.warning("Audio for " + episodeName + " cannot be found. Skipping...")
			return False


		# Download Raw Audio
		logging.info("Downloading " + episodeName)
		filename = self.dest + episodeName + ".mp3"
		audioUrl = audioElement.find("a").get("href")
		raw_audio = self.scraper.get(audioUrl, stream=True)
		try:
			with raw_audio as r:
				r.raise_for_status()
				with open(filename, 'wb') as f:
					for chunk in r.iter_content(chunk_size=8192):
						f.write(chunk)
		except Exception as e:
			logging.error(e)
			logging.error("Error while writing sound file to destination. Skipping...")
			return False
			
		# Set MP3 Tags
		file = eyed3.load(filename)
		file.initTag()
		file.tag.artist = "Dan Carlin"
		file.tag.album = "Dan Carlin's Hardcore History"
		file.tag.genre = "Podcast"
		file.tag.title = episodeName
		file.tag.track_num = trackNum

		# read cover into memory
		try:
			imagedata = open(imagePath,"rb").read()
			file.tag.images.set(3, imagedata, "image/jpeg", episodeName)
		except:
			logging.warning("Could not find cover art, continuing with no art")

		file.tag.save()
		return True

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

###### MAIN FUNCTION ######
### Parameters ###

## Destination for download
dest = sys.argv[1]
## URL for 2 week archive, get from wdcb.org/archive network traffic
url = sys.argv[2]

waitForInternetConnection(60, 5)

hh_scraper = HHScraper(url, dest)
hh_scraper.scrapeNewEpisodes()