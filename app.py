import re
import time
import urllib

import click
import requests


@click.command()
# @click.argument('song_list_file', type=click.Path(file_okay=True, exists=True))
@click.argument('song_list_file', type=click.File())
def app(song_list_file):
    """
    Iterates through song/artist lines in song_list_file and prints a line for each one that includes the first
    matching youtube video url at then end after a tab character. Fragile b/c scrapes the youtube search url rather than
    using an API, etc.

    :param song_list_file: file with one line for each song/artist, e.g., "ROLLING IN THE DEEP	Adele"
    """
    print(f"song_list_file={song_list_file}")
    results = []
    for line in song_list_file:
        urls = youtube_urls_for_query(line.strip())
        time.sleep(5)
        print('xx', line, len(urls), urls)
        results.append(f"{line}\t{urls[0] if urls else '??'}")
    for result in results:
        print(result)


def youtube_urls_for_query(query):
    """
    Scrapes youtube search results for a query and returns matching URLs in a list.

    :param query: song title, possibly with artist, etc. - passed to youtube/results. ex: "ROLLING IN THE DEEP	Adele"
    :return: list of youtube URLs matching query. they are ordered according the search HTML
    """
    encoded_query = urllib.parse.quote(query)

    # ex: "ROLLING IN THE DEEP	Adele" -> https://www.youtube.com/results?search_query=ROLLING+IN+THE+DEEP%09Adele
    query_url = f"https://www.youtube.com/results?search_query={encoded_query}"

    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    print(f"requesting: {query_url!r}")
    response = requests.get(query_url, headers=headers)
    html = response.content.decode('utf-8')
    data_context_item_ids = re.findall(r'data-context-item-id="(.*?)"', html)  # non-greedy
    print(f"{len(html)}. {len(data_context_item_ids)}: data_context_item_ids={data_context_item_ids}")
    if len(html) < 5000:  # Our systems have detected unusual traffic from your computer network.
        print(html)
    return [f'https://www.youtube.com/watch?v={data_context_item_id}' for data_context_item_id in data_context_item_ids]


if __name__ == '__main__':
    app()
