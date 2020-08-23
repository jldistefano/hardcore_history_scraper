## Hardcore History Scraper

This python script downloads all of the currently available free episodes of the Dan Carlin podcast *Hardcore History* that are not currently stored

This is best used to automatically download new episodes of the podcast as they come out

`Usage: python3 ./scraper.py [dest]`

This script is best utilized as an anacron job as follows

`7	5	hardcore.history.scraper	/usr/bin/python3 [path to scraper.py] "[save destination]"`

* 5 minute delay is useful to allow the computer to get an internet connection before attempting to scrape

Remember to have libraries available to anacron by running

`sudo -H pip3 install [lib]`

for the imports used if used with anacron, or just run below

`sudo -H pip3 install cfscrape eyed3 beautifulsoup4 requests`