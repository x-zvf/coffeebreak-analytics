#!/usr/bin/env python3



import os, math, statistics


import googleapiclient.discovery

def main():
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    youtube = googleapiclient.discovery.build(
        api_service_name, api_version, developerKey=YT_API_KEY)



    #csv_string = "Channel, subs, views, median"
    with open('channels.txt', 'r') as cf:
        channels = cf.readlines()
        for c in channels:
            c = c[:-1]
            with open("res.csv", "r") as f:
                if c in f.read():
                    print("Channel {} already checked.".format(c))
                    continue
                f.close()

            r = median_view_count(youtube, c)
            if r is None:
                print("[ERROR] failed to get channel {}".format(c))
            else:

                csv_string = "{},{},{},{},\n".format(c, r[0], r[1], r[2])
                with open("res.csv", "a") as f:
                    f.write(csv_string)

        cf.close()



def median_view_count(youtube, channel):
    """
    request = youtube.channels().list(
        part="contentDetails, statistics",
        forUsername=channel
    )
    response = request.execute() """

    #print(response)
    #if len(response["items"]) == 0:
    #    print("Could not find channel {}. Trying search".format(channel))
    request = youtube.search().list(
        part="id",
        maxResults=1,
        q=channel,
        safeSearch="none",
        type="channel"
    )
    response = request.execute()
    if len(response["items"]) == 0:
        print("Failed to find channel {}.".format(channel))
        return
    if "channelId" not in response["items"][0]["id"]:
        print("WTF IS WRONG!?: {}".format(response))
        return
    request = youtube.channels().list(
        part="contentDetails, statistics",
        id=response["items"][0]["id"]["channelId"]
    )
    response = request.execute()




    uploads_playlist_id = response["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]
    subscriber_count = response["items"][0]["statistics"]["subscriberCount"]

    video_ids = []

    request = youtube.playlistItems().list(
        part="id, contentDetails",
        playlistId=uploads_playlist_id,
        maxResults=50
    )
    while True:
        try:
            response = request.execute()
            for item in response["items"]:
                video_ids.append(item["contentDetails"]["videoId"])
            break
        except:
            print("Request failed. retrying.")

    try:
        page = response["nextPageToken"]
        request = youtube.playlistItems().list(
            part="id, contentDetails",
            playlistId=uploads_playlist_id,
            pageToken=page,
            maxResults=50
        )
        while True:
            try:
                response = request.execute()
                break
            except:
                print("Request failed. retrying.")

        for item in response["items"]:
            video_ids.append(item["contentDetails"]["videoId"])
    except:
        print("less than 51 vids.")

    #page = response["nextPageToken"]
    #while True:
    #    request = youtube.playlistItems().list(
    #        part="id, contentDetails",
    #        playlistId=uploads_playlist_id,
    #        pageToken=page,
    #        maxResults=50
    #    )

    #    while True:
    #        try:
    #            response = request.execute()
    #            break
    #        except:
    #            print("Request failed. retrying.")
    #    print(".", end="")
    #    for item in response["items"]:
    #        video_ids.append(item["contentDetails"]["videoId"])

    #    if "nextPageToken" in response:
    #        page = response["nextPageToken"]
    #    else:
    #        break
    video_ids = list(set(video_ids))
    print("\n{} video id's fetched.".format(len(video_ids)))

    video_view_counts = []


    v_id_chunks = [video_ids[x:x+100] for x in range(0, len(video_ids), 50)]

    print("{} chunks of 50".format(len(v_id_chunks)))

    for v_ids in v_id_chunks:
        request = youtube.videos().list(
            part="statistics",
            id=",".join(video_ids[:50])
        )
        while True:
            try:
                response = request.execute()
                break
            except:
                print("Request failed. retrying.")
        print(".",end="")
        for v in response["items"]:
            if "viewCount" in v["statistics"]:
                video_view_counts.append(int(v["statistics"]["viewCount"]))
            else:
                print("Fuck premium content.")

    if len(video_view_counts) == 0:
        print("No videos fetched.")
        return
    median_views = statistics.median(video_view_counts)
    print("\nMedian view count for {} with {} subscribers and {} videos: {}".format(channel,
                                                                                  subscriber_count,
                                                                                  len(video_ids),
                                                                                  median_views))
    return subscriber_count, len(video_ids), median_views


if __name__ == "__main__":
    main()