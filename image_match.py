import cv2
import numpy as np
import glob
import os
from collections import defaultdict
import pprint as pp

DATA_FOLDER = './data/'
BOUNDING_BOXES = {
	'First Pick': [
		[593, 822, 483, 552],
		[1518, 1747, 484, 551]
	],
	'Pre-bans': {
		0: [1090, 1209, 1292, 1391],
		1: [1206, 1317, 1292, 1399]
	},
	'Draft': {
		1: [550,866,708,807],
		2: [555,814,848,947],
		3: [550,782,987,1088],
		4: [550,800,1126,1226],
		5: [547,842,1268,1364],
		6: [1456,1763,705,805],
		7: [1497,1755,844,951],
		8: [1522,1760,984,1087],
		9: [1540,1758,1132,1228],
		10: [1512,1752,1273,1362]
	}
}

def area(r):
	return abs(r[0] - r[1]) * abs(r[2] - r[3])

def percentage_overlap(r1, r2):
	r3 = (
		max(r1[0], r2[0]),
		min(r1[1], r2[1]),
		max(r1[2], r2[2]),
		min(r1[3], r2[3])
	)

	if r3[0] < r3[1] and r3[3] > r3[2]:
		return area(r3) / (area(r1) + area(r2)  - area(r3)) * 100
	else:
		return 0

def match_template(template, image):
	h, w, _ = template.shape

	res = cv2.matchTemplate(template, image, cv2.TM_CCOEFF_NORMED)
	_, conf, _, pt = cv2.minMaxLoc(res)

	rect = (pt[0], pt[0] + w, pt[1], pt[1] + h)
	return rect, conf

def is_first_pick(draft):
	first_pick = os.path.join(DATA_FOLDER, 'images', 'FIRST PICK.png')
	rect, conf = match_template(cv2.imread(first_pick), draft)

	if percentage_overlap(rect, BOUNDING_BOXES['First Pick'][0]) > 0:
		first_pick = True
	elif percentage_overlap(rect, BOUNDING_BOXES['First Pick'][1]) > 0:
		first_pick = False
	else:
		raise Exception('Unable to determine first pick')

	cv2.rectangle(draft, (rect[0], rect[2]), (rect[1], rect[3]), (0, 0, 255), 2)
	return first_pick

def is_victorious(draft):
	victory = os.path.join(DATA_FOLDER, 'images', 'VICTORY.png')	
	defeat = os.path.join(DATA_FOLDER, 'images', 'DEFEAT.png')

	rect1, conf1 = match_template(cv2.imread(victory), draft)
	rect2, conf2 = match_template(cv2.imread(defeat), draft)

	if conf1 > conf2:
		victory = True
		cv2.rectangle(draft, (rect1[0], rect1[2]), (rect1[1], rect1[3]), (0, 0, 255), 2)
	else:
		victory = False
		cv2.rectangle(draft, (rect2[0], rect2[2]), (rect2[1], rect2[3]), (0, 0, 255), 2)

	return victory

def parse_match(match):
	match = os.path.join(DATA_FOLDER, 'match_history', match)

	pre_bans = os.path.join(DATA_FOLDER, 'pre_bans', '*.png')
	heroes = os.path.join(DATA_FOLDER, 'heroes', '*.png')

	pre_bans_order = defaultdict(lambda: (None, 0))
	draft_order = defaultdict(lambda: (None, 0))

	match_json = {
		'First Pick': None,
		'Pre-bans': [None, None],
		'Draft': {
			'1': [None],
			'2': [None, None],
			'3': [None, None],
			'4': [None, None],
			'5': [None, None],
			'6': [None]
		},
		'Bans': [None, None],
		'Victory': None
	}

	draft = cv2.imread(match)

	# # Parse Pre-Bans
	# for hero in glob.glob(pre_bans):
	# 	hero_name = hero.split('/')[-1].replace('.png', '')

	# 	rect, conf = match_template(cv2.imread(hero), draft)

	# 	for key, val in BOUNDING_BOXES['Pre-bans'].items():
	# 		if percentage_overlap(val, rect) > 0:
	# 			if conf > pre_bans_order[key][1]:
	# 				pre_bans_order[key] = (hero_name, conf)
	# 				cv2.rectangle(draft, (rect[0], rect[2]), (rect[1], rect[3]), (0, 0, 255), 2)

	# Parse Picks
	for hero in glob.glob(heroes):
		hero_name = hero.split('/')[-1].replace('.png', '')

		rect, conf = match_template(cv2.imread(hero), draft)

		for key, val in BOUNDING_BOXES['Draft'].items():
			if percentage_overlap(val, rect) > 0:
				if conf > draft_order[key][1]:
					draft_order[key] = (hero_name, conf)
					cv2.rectangle(draft, (rect[0], rect[2]), (rect[1], rect[3]), (0, 0, 255), 2)

	# Create JSON
	match_json['First Pick'] = is_first_pick(draft)
	match_json['Victory'] = is_victorious(draft)
	
	match_json['Pre-bans'][0] = pre_bans_order[0][0]
	match_json['Pre-bans'][1] = pre_bans_order[1][0]

	if match_json['First Pick']:
		match_json['Draft']['1'] = [draft_order[1][0]]
		match_json['Draft']['2'] = [draft_order[6][0], draft_order[7][0]]
		match_json['Draft']['3'] = [draft_order[2][0], draft_order[3][0]]
		match_json['Draft']['4'] = [draft_order[8][0], draft_order[9][0]]
		match_json['Draft']['5'] = [draft_order[4][0], draft_order[5][0]]
		match_json['Draft']['6'] = [draft_order[10][0]]
	else:
		match_json['Draft']['1'] = [draft_order[6][0]]
		match_json['Draft']['2'] = [draft_order[1][0], draft_order[2][0]]
		match_json['Draft']['3'] = [draft_order[7][0], draft_order[8][0]]
		match_json['Draft']['4'] = [draft_order[3][0], draft_order[4][0]]
		match_json['Draft']['5'] = [draft_order[9][0], draft_order[10][0]]
		match_json['Draft']['6'] = [draft_order[5][0]]

	pp.pprint(match_json)

	# Display Image
	cv2.imshow('output',draft)

	cv2.waitKey(0)
	cv2.destroyWindow('image')
	cv2.waitKey(1)

	return match_json

if __name__ == "__main__":

	# image = 'Screen Shot 2022-02-05 at 9.28.01 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.28.09 PM.png'
	image = 'Screen Shot 2022-02-05 at 9.28.24 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.28.31 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.28.40 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.28.47 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.29.00 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.29.12 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.29.23 PM.png'
	# image = 'Screen Shot 2022-02-05 at 9.29.28 PM.png'

	parse_match(image)

