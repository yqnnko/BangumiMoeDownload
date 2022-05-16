import json
import bencoder
import requests
import os
import csv

#获取Bangumi.moe下载时的文件命名
def getBangumiFileName(s: str):
    return s.translate(
        str.maketrans("\\/:*?\"<>|", "_________")
    )

#获取Windows下合法的文件命名
def getLocalDirName(s: str):
    return s.translate(
        str.maketrans("\\/:*?\"<>|","＼／：＊？＂＜＞｜")
    )

#更新CSV文件
def updateCsvFile(torrent, torrentPath: str, csvPath: str = 'output.csv'):
    #读取种子文件 获取准确的文件数量和大小
    reader = bencoder.decode(open(torrentPath,'rb').read())
    #获取CSV中的各列
    time = torrent['publish_time']
    title = getLocalDirName(torrent['title'])
    taskName = reader[b'info'][b'name'].decode()
    count = size = 0
    for file in reader[b'info'][b'files']:
        size = size + file[b'length']
        count = count + 1
    magnet = torrent['magnet']
    #写CSV行
    writer = csv.writer(open(csvPath,'a',encoding='utf-8',newline=''))
    writer.writerow([time[:10], title, taskName, count, size, magnet])

#从bangumi.moe获取种子信息
def getTorrentsFromBangumi(size: int, *keys: str):
    page = 1
    torrents = []
    url = 'https://bangumi.moe/api/torrent/search'
    payload = {"tag_id": keys, "p": page}
    while size > 0:
        res = requests.post(url, json=payload)
        if page == 1:
            size = min(json.loads(res.text)['count'], size)
        torrents = torrents + json.loads(res.text)['torrents'][:size]
        size = size - len(torrents)
    return torrents

#从bangumi.moe获取种子文件
def downloadTorrentsFromBangumi(torrents: list, path: str = 'torrents'):
    url = 'https://bangumi.moe/download/torrent/'
    for torrent in torrents:
        torrentFileName = getBangumiFileName(torrent['title']) + '.torrent'
        torrentFilePath = os.path.join(path, torrentFileName)
        downloadUrl = url + torrent['_id'] + '/' + torrentFileName
        res = requests.get(downloadUrl)
        open(torrentFilePath,'wb').write(res.content)
        updateCsvFile(torrent, torrentFilePath)


if __name__ == '__main__':
    torrents = getTorrentsFromBangumi(20, '5596b174a0b788232ee352cb')
    downloadTorrentsFromBangumi(torrents, 'torrents')
