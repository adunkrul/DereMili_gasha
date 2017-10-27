import sys
from tweepy import API, OAuthHandler, Stream, TweepError
from tweepy.streaming import StreamListener
import json
import datetime
import time
import random
import logging
from PIL import ImageFont, Imagedraw, Image

def init_auth():
  logging.info('init auth')
  key_file = open(sys.argv[1], 'r')
  key_lines = key_file.readlines()
  key_file.close()

  consumer_key = key_lines[0].replace('\n', '')
  consumer_secret = key_lines[1].replace('\n', '')
  access_token = key_lines[2].replace('\n', '')
  access_token_secret = key_lines[3].replace('\n', '')

  auth = OAuthHandler(consumer_key, consumer_secret)
  auth.set_access_token(access_token, access_token_secret)

  logging.info('done init auth')
  return auth

def make_lines(db):
  lines = db.readlines()

  val = list()

  for line in lines:
    if line == '\n':
      continue
    else:
      val.append(line)

  return val

def add_card(resultdict, card_type, card_rare):
  file = open(card_type + card_rare + '.txt', 'r')
  temp = make_lines(file)
  for i in range(len(temp)-1):
    if card_type == 'Pickup':
      resultdict['P' + card_rare].append(temp[i].split(','))
    elif not temp[i].split(',') in resultdict['P' + card_rare]
      resultdict[card_rare].append(temp[i].split(','))
  file.close()

NORMAL_GASHA = 0
COOL_TYPE_GASHA = 1
CUTE_TYPE_GASHA = 2
PASSION_TYPE_GASHA = 3
FESTIVAL_GASHA = 4

def init_card():
  key_file = open(sys.argv[1], 'r')
  key_lines = key_file.readlines()
  gasha_type = int(key_lines[len(key_lines)-1].replace('\n', ''))
  key_file.close()
  answer_dict = dict()
  answer_dict['FSSR'] = list()
  answer_dict['PSSR'] = list()
  answer_dict['SSR'] = list()
  answer_dict['PSR'] = list()
  answer_dict['SR'] = list()
  answer_dict['R'] = list()

  if gasha_type == NORMAL_GASHA:
    add_card(answer_dict, 'Pickup', 'SSR')
    add_card(answer_dict, 'Pickup', 'SR')

    add_card(answer_dict, 'Cool', 'SSR')
    add_card(answer_dict, 'Cool', 'SR')
    add_card(answer_dict, 'Cool', 'R')

    add_card(answer_dict, 'Cute', 'SSR')
    add_card(answer_dict, 'Cute', 'SR')
    add_card(answer_dict, 'Cute', 'R')

    add_card(answer_dict, 'Passion', 'SSR')
    add_card(answer_dict, 'Passion', 'SR')
    add_card(answer_dict, 'Passion', 'R')

  elif gasha_type == COOL_TYPE_GASHA:
    add_card(answer_dict, 'Cool', 'SSR')
    add_card(answer_dict, 'Cool', 'SR')
    add_card(answer_dict, 'Cool', 'R')

  elif gasha_type == CUTE_TYPE_GASHA:
    add_card(answer_dict, 'Cute', 'SSR')
    add_card(answer_dict, 'Cute', 'SR')
    add_card(answer_dict, 'Cute', 'R')

  elif gasha_type == PASSION_TYPE_GASHA:
    add_card(answer_dict, 'Passion', 'SSR')
    add_card(answer_dict, 'Passion', 'SR')
    add_card(answer_dict, 'Passion', 'R')

  else:
    add_card(answer_dict, 'Pickup', 'SSR')
    add_card(answer_dict, 'F', 'SSR')
    add_card(answer_dict, 'Cool', 'SSR')
    add_card(answer_dict, 'Cool', 'SR')
    add_card(answer_dict, 'Cool', 'R')

    add_card(answer_dict, 'Cute', 'SSR')
    add_card(answer_dict, 'Cute', 'SR')
    add_card(answer_dict, 'Cute', 'R')

    add_card(answer_dict, 'Passion', 'SSR')
    add_card(answer_dict, 'Passion', 'SR')
    add_card(answer_dict, 'Passion', 'R')

  logging.info('done init card')
  return answer_dict

def init_sche():
  logging.info('init sche')
  db_sche = open('/home/yusu/Desktop/DereMili_alarm/sche', 'r')
  lines = make_lines(db_sche)
  db_sche.close()

  logging.info('done init sche')
  return lines

def init_user():
  logging.info('init user')
  db_user = open('/home/yusu/Desktop/DereMili_alarm/user', 'r')
  lines = make_lines(db_user)
  db_user.close()

  logging.info('done init user')
  return lines

def update_user(user, game, time, alarm):
  logging.info('insert %s %s %s %s' % (user, game, time, alarm))
  db_user = open('/home/yusu/Desktop/DereMili_alarm/user', 'a')
  data = "%s %s %s %s\n" % (user, game, time, alarm)
  db_user.write(data)
  db_user.close()

  logging.info('done update user')
  return init_user()

def choose_card(gashatype, confirm):
  type_list = ['FPSSR', 'FSSR', 'PSSR', 'SSR', 'PSR', 'SR', 'R']
  if gashatype == NORMAL_gasha:
    percent_list = [0, 0, 0, 8, 22, 200, 770, 0] if confirm else [0, 0, 0, 8, 22, 24, 96, 850]
  elif gashatype < FESTIVAL_gasha:
    percent_list = [0, 0, 0, 30, 0, 970, 0] if confirm else [0, 0, 0, 30, 0, 120, 850]
  else:
    percent_list = [8, 8, 0, 44, 0, 940, 0] if confirm else [8, 8, 0, 44, 0, 120, 820]
  chosen_level = random.choices(population = type_list, weights = percent_list)[0]
  if chosen_level == 'FPSSR':
    chosen_card = random.choice(answer_dict['PSSR'])
    return chosen_card, 0
  elif chosen_level == 'R':
    chosen_card = random.choice(answer_dict['R'])
    return chosen_card, 1
  else:
    chosen_card = random.choice(answer_dict[chosen_level])
    return chosen_card, 0

class mention_listener(StreamListener):
  def init_set(self, api, sche, user, card):
    logging.info('init set')
    self.api = api
    self.sche = sche
    self.user = user
    self.card = card

  def parse_message(self, status):
    logging.info('parsing %s' % status)
    tweet = status._json
    text = str(tweet.get('text'))
    reply_user = tweet.get('user').get('screen_name')
    reply_id = tweet.get('id_str')

    logging.info('%s %s %s' % (text, reply_user, reply_id))
    return (text, reply_user, reply_id)

  def on_direct_message(self, status):
    (text, reply_user, reply_id) = self.parse_message(status)
    if '갱신' in text and reply_user == 'Segmentionfault':
      logging.info('update card list')
      list_text = text.strip().split('\n')
      list_texts = list()
      if '5' in list_text[0]:
        PickupSSR = open('PickupSSR.txt', 'w')
        PickupSR = open('PickupSR.txt', 'w')
        PickupSSR.close()
        PickupSR.close()
      else:
        for i in range(len(list_text)):
          list_texts.append(list_text[i].strip().split(','))
        key_file = open(sys.argv[1], 'a')
        key_file.write('\n' + list_text[0][1])
        key_file.close()

        position = 1
        while position < len(list_texts):
          if len(list_texts[position]) == 1:
            gasha_type = list_texts[position][0]
            position += 1
            if gasha_type == '페스':
              File_FSSR = open('FSSR.txt', 'a')
              File_PickupSSR = open('Pickup.txt', 'a')

              while len(list_texts[position]) == 5:
                File_FSSR.write('\n' + list_text[position])
                File_PickupSSR.write('\n' + list_text[position])
                position += 1
              File_FSSR.close()
              File_PickupSSR.close()

            elif gasha_type == '한정':
              dict_card = dict()
              dict_card['CoolR'] = open('CoolR.txt', 'a')
              dict_card['CoolSR'] = open('CoolSR.txt', 'a')
              dict_card['CoolSSR'] = open('CoolSSR.txt', 'a')

              dict_card['CuteR'] = open('CuteR.txt', 'a')
              dict_card['CuteSR'] = open('CuteSR.txt', 'a')
              dict_card['CuteSSR'] = open('CuteSSR.txt', 'a')
              
              dict_card['PassionR'] = open('PassionR.txt', 'a')
              dict_card['PassionSR'] = open('PassionSR.txt', 'a')
              dict_card['PassionSSR'] = open('PassionSSR.txt', 'a')

              dict_card['PickupSSR'] = open('PickupSSR.txt', 'a')
              dict_card['PickupSR'] = open('PickupSR.txt', 'a')

              while len(list_texts[position]) == 5:
                dict_card[list_texts[position][2] + list_texts[postiion][1]].write('\n' + list_text[position])
                dict_card['Pickup' + list_texts[position][1]].write('\n' + list_text[position])
                position += 1
              for item in dict_card.values():
                item.close()
            elif gasha_type == '통상':

              dict_card = dict()
              dict_card['CoolR'] = open('CoolR.txt', 'a')
              dict_card['CoolSR'] = open('CoolSR.txt', 'a')
              dict_card['CoolSSR'] = open('CoolSSR.txt', 'a')

              dict_card['CuteR'] = open('CuteR.txt', 'a')
              dict_card['CuteSR'] = open('CuteSR.txt', 'a')
              dict_card['CuteSSR'] = open('CuteSSR.txt', 'a')

              dict_card['PassionR'] = open('PassionR.txt', 'a')
              dict_card['PassionSR'] = open('PassionSR.txt', 'a')
              dict_card['PassionSSR'] = open('PassionSSR.txt', 'a')

              while len(list_texts[position]) == 5:
                dict_card[list_texts[position][2] + list_texts[postiion][1]].write('\n' + list_text[position])
                position += 1
              for item in dict_card.values():
                item.close()
          else:
            break
    else:
      logging.info('receive DM: %s %s %s' % (text, reply_user, reply_id))
      self.api.update_status(status = 'd @SegmentionFault 디엠 왔습니다.')



  def on_status(self, status):
    tweet = status._json
    (text, reply_user, reply_id) = self.parse_message(status)
    logging.info('receive mention: %s %s %s' % (text, reply_user, reply_id))

    if reply_user == 'DereMili_alarm':
      logging.info('when self-call')
      return

    if 'retweeted_status' in tweet:
      logging.info('when retweeted')
      return

    try:
      if '등록' in text:
        game = '밀리' if '밀리' in text else '데레'
        alarm = '연금' if '연금' in text else '이벤트'

        if alarm == '연금':
          time = '자정'
        else:
          time = '저녁' if '저녁' in text else '자정'

        logging.info('join: %s %s %s' % (game, alarm, time))
        for line in self.user:
          if (game in line and alarm in line and time in line and reply_user in line):
            logging.info('Already set alarm')
            self.api.update_status(status = '@' + str(reply_user) + ' 이미 등록된 알람입니다.', in_reply_to_status_id = reply_id)
            break
        else:
          logging.info('Add alarm')
          self.user = update_user(str(reply_user), game, time, alarm)
          self.api.create_friendship(reply_user)
          self.api.update_status(status = '@' + str(reply_user) + ' ' + '%s %s %s 등록되었습니다.' % (game, time, alarm), in_reply_to_status_id = reply_id)
      elif '해지' in text:
        logging.info('disjoin')
        lines = []
        with open('/home/yusu/Desktop/DereMili_alarm/user') as infile:
          for line in infile:
            if reply_user in line:
              line = ''
            lines.append(line)
        with open('/home/yusu/Desktop/DereMili_alarm/user', 'w') as outfile:
          for line in lines:
            outfile.write(line)

        self.user = init_user()
        self.api.destroy_friendship(reply_user)
        self.api.update_status(status = '@' + str(reply_user) + ' ' + '모든 알람 등록이 해지되었습니다.', in_reply_to_status_id = reply_id)
        logging.info('done disjoin')
      elif '가챠' in text:
        num_rare = 0
        answerlist = list()
        key_file = open(sys.argv[1], 'r')
        key_lines = key_file.readlines()
        gashatype = int(key_lines[len(key_lines)-1].replace('\n', ''))
        key_file.close()

        for i in range(9):
          temp_tuple = choose_card(gashatype, False)
          answerlist.append(temp_tuple[0])
          num_rare += temp_tuple[1]
        if num_rare == 9:
          answerlist.append(choose_card(gashatype, True))
        else:
          answerlist.append(choose_card(gashatype, False))



      elif '일정' in text:
        logging.info('check schedule')
        current = datetime.datetime.today()
        reply_text = '현재 일정입니다.\n'

        for line in self.sche:
          line = line.split()
          game = line[0]
          alarm = line[1]
          start = datetime.datetime.strptime(line[2], '%Y-%m-%d')
          end = datetime.datetime.strptime(line[3], '%Y-%m-%d')

          if (current > start and current < (end + datetime.timedelta(days=1))):
            logging.info('current schedule: %s %s %s %s' % (game, alarm, start.strftime('%m-%d'), end.strftime('%m-%d')))
            reply_text += '%s %s %s %s\n' % (game, alarm, start.strftime('%m-%d'), end.strftime('%m-%d'))

        self.api.update_status(status = '@' + str(reply_user) + ' ' + reply_text, in_reply_to_status_id = reply_id)
        logging.info('done check schedule')
      elif '추가' in text and str(reply_user) == 'SegmentionFault':
        logging.info('insert schedule')
        game = '밀리' if '밀리' in text else '데레'
        alarm = '이벤트' if '이벤트' in text else '연금'

        start_time = text.split()[4]
        end_time = text.split()[5]

        db_sche = open('/home/yusu/Desktop/DereMili_alarm/sche', 'a')
        data = "%s %s %s %s\n" % (game, alarm, start_time, end_time)
        db_sche.write(data)
        db_sche.close()

        self.sche = init_sche()
        self.api.update_status(status = '@' + str(reply_user) + ' ' + '%s %s %s %s 일정 등록되었습니다.' % (game, alarm, start_time, end_time), in_reply_to_status_id = reply_id)
        logging.info('done insert schedule')
      else:
        logging.info('another')
        self.api.update_status(status = '@' + str(reply_user) + ' ' + '사용방법\n일정확인 or 등록 or 해지\n데레 or 밀리\n저녁 or 자정(연금은 자정만)\n이벤트 or 연금\n등록시 팔로우, 해지는 전 알람 해지와 언팔', in_reply_to_status_id = reply_id)
    except TweepError as e:
      logging.error(e.reason)

def insert_message(dict, key, value):
  if key in dict:
    dict[key] += value
  else:
    dict[key] = value
  return dict

FORMAT = '[%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s'
logging.basicConfig(filename='/home/yusu/Desktop/DereMili_alarm/log', level=logging.INFO, datefmt='%Y %m %d %H:%M:%S', format=FORMAT)

while (True):
  logging.info('init main loop')
  auth = init_auth()
  sche = init_sche()
  user = init_user()
  card = init_card()
  api = API(auth)

  time.sleep(10)

  logging.info('init listener')
  listener = mention_listener()
  listener.init_set(api, sche, user, card)

  option = {'retry_count':3}
  stream = Stream(auth, listener)

  logging.info('init stream')
  while stream.running == False:
    logging.info('try streaming')
    time.sleep(5)
    stream.filter(track=['DereMili_alarm'], async=True)
    time.sleep(5)

  api.update_status(status = '@SegmentionFault 초기화 완료 %d' % random.choice(range(0, 1024)))
  logging.info('main loop done')
  current = datetime.datetime.today()

  if (current < datetime.datetime(current.year, current.month, current.day, 14, 20)):
    future = datetime.datetime(current.year, current.month, current.day, 14, 20)
  elif (current < datetime.datetime(current.year, current.month, current.day, 20, 20)):
    future = datetime.datetime(current.year, current.month, current.day, 20, 20)
  elif (current < datetime.datetime(current.year, current.month, current.day, 23, 20)):
    future = datetime.datetime(current.year, current.month, current.day, 23, 20)
  else:
    future = datetime.datetime(current.year, current.month, current.day, 14, 20)
    future += datetime.timedelta(days=1)

  diff = (future - current).total_seconds()
  diff += random.choice(range(0, 1200))
  logging.info('sleep: %s %s' % (str(future), str(diff)))
  time.sleep(diff)

  current = datetime.datetime.today()
  logging.info('wake up : %s' % (str(current)))
  stream.disconnect()

  messages = dict()
  for line_sche in listener.sche:
    line_sche = line_sche.split()
    print (line_sche)
    game_sche = line_sche[0]
    alarm_sche = line_sche[1]
    start_sche = datetime.datetime.strptime(line_sche[2], '%Y-%m-%d')
    end_sche = datetime.datetime.strptime(line_sche[3], '%Y-%m-%d')

    if (current < start_sche or current > (end_sche + datetime.timedelta(days=1))):
      continue

    if (current.hour == 14 and current.day == end_sche.day and alarm_sche == '연금'):
      message = '%s 가챠 갱신일\n' % game_sche
    elif (current.hour == 20 and alarm_sche == '이벤트'):
      message = '%s 이벤트 저녁 알림\n' % game_sche
    elif (current.hour == 20 and current.day == end_sche.day and alarm_sche == '이벤트'):
      message = '%s 이벤트 끝나는 알림\n' % game_sche
    elif (current.hour == 23 and current.day != end_sche.day and alarm_sche == '이벤트'):
      message = '%s 이벤트 자정 알림\n' % game_sche
    elif (current.hour == 23 and current.day != end_sche.day and alarm_sche == '연금'):
      message = '%s 날짜 변경 알림\n' % game_sche
    else:
      continue

    logging.info('message : %s' % message)
    messages = insert_message(messages, 'DereMili_alarm', message)

    for line_user in listener.user:
      line_user = line_user.split()
      print (line_user)
      user_user = line_user[0]
      game_user = line_user[1]
      time_user = line_user[2]
      alarm_user = line_user[3]

      if (current.hour == 14 and current.day == end_sche.day and alarm_sche == '연금' and alarm_user == '연금' and game_sche == game_user):
        message = '%s 가챠 갱신일\n' % game_user
      elif (current.hour == 20 and alarm_sche == '이벤트' and alarm_user == '이벤트' and game_sche == game_user and time_user == '저녁'):
        message = '%s 이벤트 저녁 알림\n' % game_user
      elif (current.hour == 20 and current.day == end_sche.day and alarm_sche == '이벤트' and alarm_user == '이벤트' and game_sche == game_user):
        message = '%s 이벤트 끝나는 알림\n' % game_user
      elif (current.hour == 23 and current.day != end_sche.day and alarm_sche == '이벤트' and alarm_user == '이벤트' and game_sche == game_user and time_user == '자정'):
        message = '%s 이벤트 자정 알림\n' % game_user
      elif (current.hour == 23 and current.day != end_sche.day and alarm_sche == '연금' and alarm_user == '연금' and game_sche == game_user):
        message = '%s 날짜 변경 알림\n' % game_user
      else:
        continue
      logging.info('user message : %s %s' % (user_user, message))
      messages = insert_message(messages, user_user, message)

  for key in messages:
    try:
      print(messages[key])
      logging.info('Send message: %s, %s' % (key, messages(key)))
      if key == 'DereMili_alarm':
        api.update_status(status = messages[key] + '\n%d' % random.choice(range(0,1024)))
      else:
        api.update_status(status = '@' + key + '\n' + messages[key])
    except TweepError as e:
      logging.error(e.reason)
api.update_status(status = '@' + key + '\n알람이 너무 많이 중복 등록되어 알람 메시지가 140자가 넘어 에러가 발생하였습니다. 해지해주세요.')
