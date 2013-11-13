import codecs
import pymongo
import csv
import json
import datetime
from dateutil.parser import parse
import requests
import logging
import re
import os
import weibo_settings
import weibo_module
import sys



###
#let's #print a log of all deleted posts, with the repost count/checked time following as pairs. so:
# post_id, user id, etc....... and then , unixepoch, repost count, unixepoch, repost count.... 

#if exclude_error_code = false, use error_code as filter
def csvize_repost_timeline(csv_filename, type="deleted", error_code=-1, exclude_error_code=False):

	nowdatetime = weibo_module.get_current_chinatime()

	if type == "deleted":
		query_post_ids = weibo_module.get_deleted_postids(error_code, exclude_error_code)
	else:
		query_post_ids = weibo_module.get_all_postids()
#		query_post_ids = query_post_ids[:10]
		print query_post_ids

	num_query_posts = len(query_post_ids)

	#if we're not tracking any posts, get out of there
	if (num_query_posts <= 0):
		return

	## OPEN A FILE
	with codecs.open(csv_filename, "wb") as wf:

		wf.write("[ " + "\n")

		#iterate through posts
		postno = 0
		for this_post_id in query_post_ids:

			postno += 1
			print "\n==WRITING (", postno, " / ", num_query_posts, ") POST #=========", this_post_id

			# okay first we get the initial post
			this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

			# and then we scan the rest 
			this_post_all_logs =  weibo_module.get_all_posts(this_post_id)

			# and then we amass a logline 
			this_log_list = []
			for this_log in this_post_all_logs:
				if 'post_repost_count' in this_log and this_log["post_repost_count"] <> None and this_log["checked_at"] <> None:
					this_pair_dict = {}
					this_pair_dict["checked_at"] = str(this_log["checked_at"])
					this_pair_dict["post_repost_count"] = int(this_log["post_repost_count"])

					this_log_list.append(this_pair_dict)

			#get jsonline array
			jsonline = weibo_module.make_jsonlist_from_post(this_post)

			#merge logline into 
			jsonline['post_repost_log'] = this_log_list

			#wf.write(json.dumps(jsonline, ensure_ascii=False))
			wf.write(json.dumps(jsonline))

			if postno != num_query_posts:
				wf.write(", ")

			wf.write("\n")

		wf.write(" ]" + "\n")

#################################
#################################
#################################
#################################


#our process
#grab all the deleted posts
#massage to CSV!
#csvize_deleted_repost_timeline(weibo_settings.all_log_csv_filename, 10023, True)
if(len(sys.argv) > 1 and sys.argv[1] == "-all"):#
	csvize_repost_timeline(weibo_settings.all_log_csv_filename, "all")
else:
#	csvize_repost_timeline(weibo_settings.deleted_log_csv_filename, "deleted", 10023, True)
	csvize_repost_timeline(weibo_settings.deleted_log_json_filename, "deleted", 10023, True)

#deleted_in_sample()


