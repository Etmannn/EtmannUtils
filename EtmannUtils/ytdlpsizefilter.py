import itertools
import json
import os
import subprocess
import sys

# This function gets all the required data about the video you are trying to download
def _get_data(link: str):
    # Returns all the information about the video and the streams as a json
    result = subprocess.run(['yt-dlp', '-F', '-j', link], capture_output=True, text=True)

    if result.returncode != 0:
        return 'Failed to get data'

    output = result.stdout
    output = output.split('\n')
    data = json.loads(output[-2])

    format_id = [x.get('format_id') for x in data['formats']]
    filesize = [x.get('filesize', None) for x in data['formats']]

    video_ext = [x.get('video_ext') for x in data['formats']]
    audio_ext = [x.get('audio_ext') for x in data['formats']]

    video_data = []
    audio_data = []

    # Sorts video and audio stream data into seperate lists
    for i in range(len(format_id)):
        if video_ext[i] != 'none':
            video_data.append(tuple([format_id[i], filesize[i]]))

        if audio_ext[i] != 'none':
            audio_data.append(tuple([format_id[i], filesize[i]]))

    return [video_data, audio_data]


# This function calls the _get_data() function and downloads the video to the specified directory
def download(link: str, filetype: str, maxsize: float, dir: str):
    data = _get_data(link)
    dir = dir.replace('\\', '\\\\')

    if data == 'Failed to get data':
        return 'Download Failed', None

    # Seperates the filesizes and ids of both video and audio stream data
    vfilesize = [x[1] for x in data[0]]
    afilesize = [x[1] for x in data[1]]
    vid = [x[0] for x in data[0]]
    aid = [x[0] for x in data[1]]

    if filetype == 'video':
        # Makes a list of combinations of all the possible video and audio stream sizes
        combinations = list(itertools.product(vfilesize, afilesize))

        options = []
        for v, a in combinations:
            try:
                # Converts the filesize from kibibytes to megabytes
                mbsize = (v + a) / 1000000

                # If the combination of filesizes is less than maxsize then it is added to a list
                if mbsize < maxsize:
                    options.append(tuple([mbsize, v, a]))

            except TypeError:
                pass

        # Finds the biggest combination in the list of valid combinations and if there is one.
        if len(options) > 0:
            sorted_options = sorted(options, key=lambda x: x[0])
            final_option = sorted_options[-1]
            # Selects the correct streams and saves a reference of the format_id to call later
            format_id = f'{vid[vfilesize.index(final_option[1])]}+{aid[afilesize.index(final_option[2])]}'
            f = len(os.listdir(dir))
            # Full command with format_id
            command = f'yt-dlp -f {format_id} --merge-output-format mp4 -o {dir}/{f}_%(title)s.%(ext)s {link}'

        else:
            return 'Video too big', None

    if filetype == 'audio':
        options = []
        for a in afilesize:
            try:
                mbsize = a / 1000000

                if mbsize < maxsize:
                    options.append(a)
            except TypeError:
                pass

        if len(options) > 0:
            final_option = max(options)
            format_id = aid[afilesize.index(final_option)]
            f = len(os.listdir(dir))
            command = f'yt-dlp -f {format_id} -x --audio-format mp3 -o {dir}/{f}_%(title)s.%(ext)s {link}'
        else:
            return 'Video too big', None

    # Run the previously defined command and stores the result in the variable result
    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        # Returns the name of the most recently downloaded file
        f = len(os.listdir(dir)) - 1
        file = os.listdir(dir).index([x for x in os.listdir(dir) if x.startswith(f'{f}_')][0])
        return 'Download Complete', os.listdir(dir)[file]
    else:
        return 'Download Failed', None


# handles if the program is run directly or run as a command with argument
if __name__ == '__main__':
    try:
        link = sys.argv[1]
    except IndexError:
        link = input("input youtube link: ")

    try:
        filetype = sys.argv[2]
    except IndexError:
        filetype = input("video or audio?: ")

    try:
        maxsize = float(sys.argv[3])
    except IndexError:
        maxsize = float(input("input maximum size: "))

    try:
        dir = sys.argv[4]
    except IndexError:
        dir = input("Input directory: ")

    dir = dir.replace('\\', '\\\\')

    print(download(link=link, filetype=filetype, maxsize=maxsize, dir=dir))

__all__ = ['download']
