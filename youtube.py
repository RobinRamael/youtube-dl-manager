#! /usr/bin/env python


#    youtube-dl-manager

#    Downloads new youtube-videos in your subscription to a directory.
#    by Robin Ramael <robin.ramael@gmail.com>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

import urllib2, re, PyRSS2Gen,  feedparser, sqlite3, os, urlparse, subprocess, sys



try:
    propfile = file('./youtube.properties', 'r')
except:
    print("No propertiesfile found, please copy the youtube.properties.example file and fill out the fields.")
    exit(1)

try:
    props = dict([tuple(l.strip().split('=')) for l in propfile.readlines()])
except Exception as e:
    print("malformed properties file, please see the example provided")
    print e
    exit(1)

try:
    VIDEODIR = props['video_dir']
    USERNAME = props['username']
except:
    print("malformed properties file: video_dir or username missing. Please see the example provided.")
    exit(1)


DBDIR = props['db_dir'] if 'db_dir' in props else VIDEODIR

FEEDURL = "http://gdata.youtube.com/feeds/base/users/" + USERNAME + "/newsubscriptionvideos"

DBFILE = VIDEODIR + "/videos.db"



class YTVideo:
    def __init__(self, rss_item):
        self.url  = rss_item['link']
        self.id = urlparse.parse_qs(urlparse.urlparse(self.url).query)['v'][0]
        self.title  = rss_item['title']
        self.author = rss_item['author']
        self.publishdate = rss_item['date_parsed']

    def should_be_downloaded(self, connection):
        c = connection.cursor()
        c.execute('''SELECT count(*) FROM videos WHERE id = ?''', [self.id])
        cnt = c.fetchone()[0]
        return cnt == 0

    def download(self, connection):
        if self.should_be_downloaded(connection):
            print 'downloading', self.title, self.author, self.url
            self.download_no_check(connection)
        else: print "already downloaded", self.title, self.author, self.id

    def download_no_check(self, connection):
        cmd = ["youtube-dl",
             #"--restrict-filenames",
             "-o", "%(uploader)s - %(title)s.%(ext)s",
             self.url]
        print " ".join(cmd)
        child = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE)

        streamdata = child.communicate()[0]

        # add to db only when download is succesfull
        if child.returncode == 0:
            c = connection.cursor()
            if self.publishdate:
                date_as_str = str(self.publishdate)
            else: date_as_str = ""
            c.execute("INSERT INTO videos values (?, ?);", (self.id, date_as_str))
        else: print 'download of', self.id, 'failed'


def download_all_in_feed():
    feed = feedparser.parse(FEEDURL)

    db = sqlite3.connect(DBFILE)

    c = db.cursor()

    c.execute('''CREATE TABLE IF NOT EXISTS videos(id text, pubdate text)''')
    c.execute('''SELECT count(*) FROM videos''')
    if c.fetchone()[0] > 0:
        c.execute("SELECT max(pubdate) FROM videos where pubdate not like ''")
        last_download_date = c.fetchone()[0]
        #print last_download_date
    else: last_download_date = None

    videos_in_feed = [YTVideo(item) for item in feed['items']]

    os.chdir(VIDEODIR)

    for video in videos_in_feed:
        video.download(db)


    db.commit()
    db.close()


def main():
    if not os.path.exists(VIDEODIR):
        os.makedirs(VIDEODIR)

    if not os.path.exists(DBDIR):
        os.makedirs(DBDIR)

    os.chdir(VIDEODIR)

    if len(sys.argv) == 1:
        download_all_in_feed()
    else:
        db = sqlite3.connect(DB_FILE)
        for arg in sys.argv[1:]:
            video = YTVideo({'title':'', 'link': arg, 'author':'', 'date_parsed': ''})
            video.download(db)

        db.commit()
        db.close()



if __name__ == '__main__':
    main()
