import itertools
import json
import os
import subprocess
import sys

# set this to the directory you want to download to
# make sure to use forward slashes or double back slashes
dir = ''

def get_data(link: str) -> list[list]:
    result = subprocess.run(['yt-dlp', '-F', '-j', link], capture_output=True, text=True)

    if result.returncode == 0:
        output = result.stdout
        output = output.split('\n')
        data = json.loads(output[-2])

        format_id = [x.get('format_id') for x in data['formats']]
        filesize = [x.get('filesize', None) for x in data['formats']]

        video_ext = [x.get('video_ext') for x in data['formats']]
        audio_ext = [x.get('audio_ext') for x in data['formats']]

        video_data = []
        audio_data = []

        for i in range(len(format_id)):
            if video_ext[i] != 'none':
                video_data.append(tuple([format_id[i], filesize[i]]))

            if audio_ext[i] != 'none':
                audio_data.append(tuple([format_id[i], filesize[i]]))

        return [video_data, audio_data]
    else:
        print('command failed.')


def download(link: str, filetype: str, maxsize: float):
    data: list[list] = get_data(link)

    vfilesize = [x[1] for x in data[0]]
    afilesize = [x[1] for x in data[1]]
    vid = [x[0] for x in data[0]]
    aid = [x[0] for x in data[1]]

    if filetype == 'video':
        combinations = list(itertools.product(vfilesize, afilesize))

        options = []
        for v, a in combinations:
            try:
                mbsize = (v + a) / 1000000

                if mbsize < maxsize:
                    options.append(tuple([mbsize, v, a]))

            except TypeError:
                pass

        if len(options) > 0:
            sorted_options = sorted(options, key=lambda x: x[0])
            final_option = sorted_options[-1]
            format_id = f'{vid[vfilesize.index(final_option[1])]}+{aid[afilesize.index(final_option[2])]}'
            command = f'yt-dlp -f {format_id} --merge-output-format mp4 -o {dir}/%(title)s.%(ext)s {link}'

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
            command = f'yt-dlp -f {format_id} -x --audio-format mp3 -o {dir}/%(title)s.%(ext)s {link}'
        else:
            return 'Video too big', None

    result = subprocess.run(command, capture_output=True, text=True)

    if result.returncode == 0:
        return 'Download Complete', os.listdir(dir)[0]
    else:
        return 'Download Failed', None


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

    print(download(link=link, filetype=filetype, maxsize=maxsize))
