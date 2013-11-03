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




#if exclude_error_code = false, use error_code as filter
def csvize_deleted_unique(csv_filename, error_code=-1, exclude_error_code=False):

	nowdatetime = weibo_module.get_current_chinatime()

	deleted_post_ids = weibo_module.get_deleted_postids(error_code, exclude_error_code)
	num_dead_posts = len(deleted_post_ids)

	#if we're not tracking any posts, get out of there
	if (num_dead_posts <= 0):
		return

	## OPEN A FILE
	with codecs.open(csv_filename, "wb", "utf-16") as wf:

		#write csv header
		csv_header = weibo_module.get_csv_header()
		wf.write(csv_header + "\n")
		#print csv_header

		#iterate through posts
		for this_post_id in deleted_post_ids:

			this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

			csvline = weibo_module.make_csvline_from_post(this_post)

		
			csvline = map((lambda x: unicode(x)), csvline)

			#not csv, this is our delimiter now
			csvline = weibo_settings.delim.join(csvline)

#			#print csvline
			wf.write(csvline + "\n")



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
	with codecs.open(csv_filename, "wb", "utf-16") as wf:

		#write csv header
		csv_header = weibo_module.get_csv_header()
		wf.write(csv_header + "\n")

		#iterate through posts
		postno = 0
		for this_post_id in query_post_ids:

			postno += 1
			print "\n==WRITING (", postno, " / ", len(query_post_ids), ") POST #=========", this_post_id

			# okay first we get the initial post
			this_post = weibo_module.merge_deleted_from_new_old(this_post_id)

			# and then we scan the rest 
			this_post_all_logs =  weibo_module.get_all_posts(this_post_id)

			# and then we amass a logline 
			this_log_dict = {}
			for this_log in this_post_all_logs:
				if 'post_repost_count' in this_log and this_log["post_repost_count"] <> None and this_log["checked_at"] <> None:
					this_log_dict[str(this_log["checked_at"])] = int(this_log["post_repost_count"])

			#get jsonline array
			jsonline = weibo_module.make_jsonlist_from_post(this_post)

			#merge logline into 
			jsonline['log_line'] = this_log_dict

			#wf.write(json.dumps(jsonline, ensure_ascii=False))
			wf.write(json.dumps(jsonline))

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

