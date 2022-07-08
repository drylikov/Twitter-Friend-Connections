# from tqdm import tqdm
from os.path import isfile, join
from os import listdir
import numpy as np
import argparse
import tweepy
import queue
import time
import os

## get args
parser = argparse.ArgumentParser(description=
    "Simple Friends Conections Downloader", usage='%(prog)s -n <screen_name> [options]')

parser.add_argument('-n', '--name', required=False, metavar="screen_name",
                    help='target screen_name')

parser.add_argument('-l', '--limit', metavar='N', type=int, default=10,
                    help='limit the number of tweets to retreive (default=10)')

parser.add_argument('-p', dest='saveProfile', action='store_const', const=True, default=False,
                    help='set to download profiles infos!')

parser.add_argument('-i', metavar='inputPath', default="./downloaded",
                    help='input download folder')

parser.add_argument('-o', metavar='outputPath', default="./profiles",
                    help='output profile folder')

args = parser.parse_args()

from secrets import consumer_key, consumer_secret, access_token, access_token_secret
auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)

def getFriendsId(api, id):
    itr = tweepy.Cursor(api.friends_ids, id=id).items()
    res = []
    while True:

        try:
            for friendId in itr:
                res.append(friendId)
            return res

        except tweepy.TweepError as e:
            if e.response.status_code == 429:
                print("sleep for 5Min! -> " + time.ctime())
                time.sleep(5 * 60)
                print("continue! -> " + time.ctime())
            else:
                raise e

def bfs(api, head, maxDepth):
    bfsQ = queue.deque( [(head, 0)] )

    while True:
        try:
            while len(bfsQ) != 0 and bfsQ[0][1] < maxDepth:
                nodeId = bfsQ.popleft()
                print("getting userId: ", nodeId)

                if not os.path.isfile("./downloaded/" + str(nodeId[0]) + ".npy"):
                    friendsId = getFriendsId(api, nodeId[0])
                    np.save("./downloaded/" + str(nodeId[0]), np.array(friendsId))
                    for friendId in friendsId:
                        bfsQ.append( (friendId, nodeId[1]+1) )
        except:
            print("bad error!")
            np.save("bfsQ", np.array(bfsQ))

def downloadProfile(api, outputPath, id):
    while True:
        try:
            profileData = api.get_user(id=id)
            np.save(outputPath + '/' + str(id), np.array(profileData))
            print("new profile added: ", id)
            return
        except tweepy.TweepError as e:
            if e.response.status_code == 429:
                print("sleep for 5Min! -> " + time.ctime())
                time.sleep(5 * 60)
                print("continue! -> " + time.ctime())
            else:
                raise e

def checkNewProfile(api, inputPath, outputPath):
    files = [f for f in listdir(inputPath) if isfile(join(inputPath, f))]
    for f in files:
        if not os.path.isfile(outputPath + '/' + f):
            if f.find('.npy') != -1:
                print(f)
                downloadProfile(api, outputPath, f[:f.find('.npy')])


if not args.saveProfile:
    user_info = api.get_user(screen_name=args.name)
    bfs(api, user_info._json['id'], args.limit)
else:
    while True:
        checkNewProfile(api, args.i, args.o)
        print("checking off!" + time.ctime())
        time.sleep(5 * 60)
        print("start checking!" + time.ctime())
