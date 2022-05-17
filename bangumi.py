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
    count = size = 0
    if b'files' in reader[b'info'].keys():
        for file in reader[b'info'][b'files']:
            size = size + file[b'length']
            count = count + 1
    else:
        count = 1
        size = reader[b'info'][b'length']
    #从bangumi返回的torrent中读取其他列
    time = torrent['publish_time']
    title = getLocalDirName(torrent['title'])
    taskName = reader[b'info'][b'name'].decode()
    magnet = torrent['magnet']
    #写CSV行
    writer = csv.writer(open(csvPath,'a',encoding='utf-8',newline=''))
    writer.writerow([time[:10], title, taskName, count, size, magnet])

#根据标签从bangumi.moe搜索种子信息
def getTorrentsFromBangumiByTags(size: int, *tags: str):
    torrents = []
    url = 'https://bangumi.moe/api/torrent/search'
    payload = {"tag_id": tags, "p": 1}
    while size > len(torrents):
        res = requests.post(url, json=payload)
        if payload['p'] == 1:
            size = min(json.loads(res.text)['count'], size)
        torrents = torrents + json.loads(res.text)['torrents'][:size]
        payload['p'] = payload['p'] + 1
    return torrents

#根据关键字从bangumi.moe搜索种子信息
def getTorrentsFromBangumiByKey(size: int, key: str):
    torrents = []
    url = 'https://bangumi.moe/api/v2/torrent/search'
    payload = {"query": key, "p": 1}
    while size > len(torrents):
        res = requests.post(url, json=payload)
        if payload['p'] == 1:
            size = min(json.loads(res.text)['count'], size)
        torrents = torrents + json.loads(res.text)['torrents'][:size]
        payload['p'] = payload['p'] + 1
    return torrents

#从bangumi.moe获取种子文件
def downloadTorrentsFromBangumi(torrents: list, path: str = 'torrents'):
    if not os.path.exists(path):
        os.mkdir(path)
    url = 'https://bangumi.moe/download/torrent/'
    for torrent in torrents:
        torrentFileName = getBangumiFileName(torrent['title']) + '.torrent'
        torrentFilePath = os.path.join(path, torrentFileName)
        downloadUrl = url + torrent['_id'] + '/' + torrentFileName
        res = requests.get(downloadUrl)
        open(torrentFilePath,'wb').write(res.content)
        updateCsvFile(torrent, torrentFilePath)


if __name__ == '__main__':
    size = int(input('请输入要抓取的种子数量 (默认 999): ') or 999)
    tags = input('请输入标签tags,多个标签以逗号隔开 (默认 624774a470e8f89b23a1855e): ').split(',') or '624774a470e8f89b23a1855e'
    key = input('请输入关键字 (默认 VCB): ') or 'VCB'

    torrents = getTorrentsFromBangumiByTags(size, tags)
    #torrents = getTorrentsFromBangumiByKey(size, key)
    downloadTorrentsFromBangumi(torrents, 'torrents')
