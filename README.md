# youtube-dl-manager

youtube-dl-manager automatically downloads all new videos in your subscription feed to a directory. I wrote this because I only had access to a fast internet connection at certain times and wanted to download my new videos for later watching.

## usage

Download all new videos in your subscription feed to your video directory:
    python youtube.py

Download a specific video to your directory:
    python youtube.py <youtube-url> (<youtube-url> ...)


## setup and requirements

All commands require you to have filled out the `youtube.properties.example` file and moved it to `youtube.properties`

For now this project requires [youtube-dl](http://rg3.github.com/youtube-dl/), which is a great project in itself. to be installed and on your path. this is also written in python so I might just include it in the project one day, but I'm not sure how. youtube-dl does not support importing and isn't on pip, so...

Unless you delete the `videos.db` file, a video you already downloaded will not be downloaded again, even if you deleted it from the folder.


## License

this project is licensed under the GPL.
