import urllib

import click
import requests


API_KEY = 'AIzaSyAqckyDHpkDcDIz3A_Zvf2xQfJFrxg6ozk'


@click.command()
@click.argument('song_list_file', type=click.File())
def app(song_list_file):
    """
    Iterates through song/artist lines in song_list_file and prints a line for each one that includes the first
    matching youtube video url.

    :param song_list_file: file with one line for each song/artist, e.g., "ROLLING IN THE DEEP	Adele"
    """
    click.echo(f"song_list_file={song_list_file}")
    results = []  # 3-tuples: (line, title, video_url)
    for line in song_list_file:
        line = line.strip()
        video_id, title = youtube_search_first_hit(line)
        video_url = f'https://www.youtube.com/watch?v={video_id}'
        results.append((line, title, video_url))
    for line, title, video_url in results:
        click.echo(f"{line}\t{title}\t{video_url}")


def youtube_search_first_hit(query):
    """
    Calls the youtube search API to get the first hit for `query`.

    :param query: free-form text that should include a song title at a minimum, but including artist will yield better
        results
    :return: 2-tuple: (video_id, title) of the first matching hit
    """
    encoded_query = urllib.parse.quote(query)
    api_url = 'https://www.googleapis.com/youtube/v3/search'
    max_results = 1  # default = 5
    # limit the fields returned to minimize quota impact. we only want:
    # - items > id > videoId
    # - items > snippet > title
    fields = 'items(id,snippet(title))'
    search_url = f'{api_url}?part=snippet&fields={fields}&maxResults={max_results}&q={encoded_query}&type=video&key={API_KEY}'
    headers = {'Accept': 'application/json'}
    response = requests.get(search_url, headers=headers)
    response_json = response.json()
    if response.status_code != 200:
        click.echo('error!', response, response_json['error'], err=True)
        return

    response_items = response_json['items']  # up to max_results of them
    if not response_items:
        click.echo('no items!', err=True)
        return

    video_id = response_items[0]['id']['videoId']
    title = response_items[0]['snippet']['title']
    return video_id, title


if __name__ == '__main__':
    app()
