import scrapetube
import gspread
from google.oauth2.service_account import Credentials
from datetime import datetime, timezone
import json


class Util:
    def __init__(self, logger):
        self.logger = logger
        self.SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        self.CREDS = Credentials.from_service_account_file('google_creds.json', scopes=self.SCOPE)
        self.file = open("my_creds.json", 'r', encoding='utf-8')
        self.data = json.load(self.file)
        self.URL = self.data["URL"]
        self.TABLE = self.data["TABLE"]
        self.BOT_TOKEN = self.data["BOT_TOKEN"]
        self.CHAT_IDS = self.data["CHAT_IDS"]
        self.LOGS_ID = self.data["CHAT_IDS"]["logs"]
        self.PREFIX = "https://www.youtube.com/watch_videos?video_ids="
        self.SIZE = 20
        self.NOW = datetime.now()

    def read_file(self, file_path):
        client = gspread.authorize(self.CREDS)
        sheet = client.open_by_url(file_path)
        worksheet = sheet.worksheet(self.TABLE)
        data = worksheet.get_all_values()

        worksheet = sheet.worksheet('STRING')
        msg = [item[0] for item in worksheet.get_all_values()]

        worksheet = sheet.worksheet('Categories')
        categories = {item[0]: item[1] for item in worksheet.get_all_values()[1:]}

        worksheet = sheet.worksheet('exercises')
        exs = worksheet.get_all_values()
        exs_out = dict()
        i = 0
        for cat in categories:
            exs_out[cat] = exs[(self.NOW.day + 12//len(categories)*i) % 12][0]
            i += 1

        out = [{'Nickname': row[0], 'Channels': row[1], 'ShortsQnt': row[2], 'Category': row[3]} for row in data[1:]]
        return out, exs_out, msg, categories

    def get_videos(self, data, categories):
        ans = {key: [] for key in categories.keys()}
        for row in data:
            videos = scrapetube.get_channel(channel_username=row['Channels'], content_type='videos')
            shorts = []
            if int(row['ShortsQnt']) != 0:
                shorts = scrapetube.get_channel(channel_username=row['Channels'], content_type='shorts')

            self.logger.info(row)
            try:
                for vid in videos:
                    try:
                        if vid.get("upcomingEventData", None) is not None:
                            continue
                        length = vid['lengthText']['simpleText'].split(':')
                        if len(length) == 1 or len(length) == 2 and (int(length[0]) < 11 or int(length[0]) == 11 and int(length[1]) == 00):
                            ans[row['Category']].append(vid['videoId'])
                            break
                    except:
                        self.logger.warning("Video error")
                        continue
            except:
                self.logger.warning("Video error")
                pass
            try:
                shorts_limit = int(row['ShortsQnt'])
                shorts_count = 0
                for vid in shorts:
                    try:
                        if vid['viewCountText']['accessibility']['accessibilityData'] is not None:
                            ans[row['Category']].append(vid['videoId'])
                            shorts_count += 1
                            if shorts_count == shorts_limit:
                                break
                    except:
                        self.logger.warning("Short error")
                        continue
            except:
                self.logger.warning("Short error")
                pass
        return ans

    def create_playlists(self, vids):
        playlists = []
        iter = 0
        playlist = self.PREFIX
        for vid in vids:
            playlist += f"{vid},"
            iter += 1
            if iter == self.SIZE:
                playlists.append(playlist[:-1])
                playlist = self.PREFIX
                iter = 0
        if iter != 0:
            playlists.append(playlist[:-1])
        return playlists

    def create_message(self, playlists, msg, exs, ref):
        ans = msg[0]
        for i in range(len(playlists)):
            ans += f"\n\n✔️ <a href='{playlists[i]}'>Плейлист #{i+1} от {self.NOW.date().strftime("%d/%m/%Y")}</a>"
        ans += (f"\n\n{msg[1]}"
                f"<i>{exs}</i>"
                f"{msg[2]}<a href='{ref}'>Гугл форму</a>"
                f"\n{msg[3]}")
        return ans

    def all_way(self):
        msgs = dict()
        file, exs, msg, cats = self.read_file(self.URL)
        vids_ids = self.get_videos(file, cats)
        for cat in cats:
            playlist = self.create_playlists(vids_ids[cat])
            msgs[cat] = self.create_message(playlist, msg, exs[cat], cats[cat])
        return msgs
