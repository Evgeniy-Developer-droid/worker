import time
import psycopg2
import pathlib
import asyncio
from os import listdir
from os.path import isfile, join
import importlib.util
import json
import requests
import config
from loguru import logger
import sys

logger.add(sys.stderr, format="{time} {level} {message}", filter="my_module", level="DEBUG")
logger.add("log_file.log", retention="10 days")


conn = psycopg2.connect(dbname=config.DB_NAME, user=config.DB_USER, 
                        password=config.DB_PASS, host='db')
cursor = conn.cursor()

WORK_DIR = pathlib.Path().resolve()
tests_dirs = [f for f in listdir(str(WORK_DIR)+'/tests/') if f[0] != '_']


# cursor.execute("DROP TABLE statistic, job_stack")
# conn.commit()

async def get_wait_job():
	"""Get all jobs with status `waiting` """
	try:
		cursor.execute("SELECT * FROM job_stack WHERE status = 'waiting' ORDER BY priority ASC")
	except psycopg2.errors.UndefinedTable:
		return []
	# cursor.execute("SELECT * FROM job_stack")
	return cursor.fetchall()


async def get_statistic():
	"""Get statistic object if doesnt exist - create him"""
	cursor.execute('SELECT * FROM statistic WHERE id = 1')
	statistic = cursor.fetchone()
	if not statistic: # if row doesnt exist
		logger.debug("Create statistic statement")
		cursor.execute("""INSERT INTO statistic VALUES (1, 0, 0, 0, 0, 0)""")
		conn.commit()
		cursor.execute('SELECT * FROM statistic WHERE id = 1')
		statistic = cursor.fetchone()
	return statistic


async def change_status(id:int, status:dict):
	"""Change status for job object"""
	cursor.execute("UPDATE job_stack SET status = %s WHERE id = %s", (status, id))
	conn.commit()


async def update_job(id:int, result:dict, status:str):
	"""Update job - set result json and status"""
	cursor.execute("UPDATE job_stack SET results = %s, status = %s WHERE id = %s", (json.dumps(result), status, id))
	conn.commit()


async def update_statistic(key:str, time_delay:int = 0):
	"""Update statistic"""
	stat = await get_statistic()
	if key == "before":
		cursor.execute("UPDATE statistic SET queue = %s, in_progress = %s WHERE id = 1", (stat[3]-1, stat[2]+1))
	if key == "after":
		new_sum = float(stat[-1]) + time_delay
		average_time = (new_sum) / (stat[1]+1)
		cursor.execute("""UPDATE statistic SET processed = %s, in_progress = %s, 
			average_processing_time = %s, sum_time = %s WHERE id = 1""", 
			(stat[1]+1, stat[2]-1, str(average_time), str(new_sum)))
	conn.commit()


async def send_request(id:int, data:dict, token:str):
	"""Send result tests to callback url"""
	cursor.execute("SELECT * FROM job_stack WHERE id = {}".format(id))
	job = cursor.fetchone()
	try:
		headers = {"Authorization": "Bearer {}".format(token), "Content-Type": "application/json"}
		r = requests.post(job[5], json.dumps(data), headers=headers)
		print("success - "+str(id))
	except requests.exceptions.ConnectionError:
		logger.warning("Error send! Job {} didn`t send callback. Server has been broken or url callback is not valid!".format(id))


async def main():
	async def execute_test(job_data:tuple):
		result = dict()
		result['results'] = dict()
		result['job'] = {"id":job_data[1], "url":job_data[2], "creation_date":job_data[7], "processing_time":0}
		await change_status(job_data[0], "performed")
		await update_statistic('before')
		time_point_start = time.time()

		for test_module in tests_dirs:
			result['results'][test_module] = dict()
			try:
				spec = importlib.util.spec_from_file_location(test_module, str(WORK_DIR)+'/tests/'+test_module+'/tests.py')
				foo = importlib.util.module_from_spec(spec)
				spec.loader.exec_module(foo)
				try:
					class_object = getattr(foo, test_module)
					methods = [method for method in dir(class_object) if method.startswith('test_')]
					for method in methods:
						class_method = getattr(class_object, method)
						try:
							result['results'][test_module][method] = class_method(foo, job_data[2])
						except TypeError:
							logger.warning("{} - TypeError".format(test_module))
				except AttributeError:
					logger.warning("{} - AttributeError".format(test_module))
			except FileNotFoundError:
				logger.warning("File {} not found".format(test_module))

		time_point_finish = (time.time()) - time_point_start
		result['job']['processing_time'] = time_point_finish
		await update_job(job_data[0], result, "done")
		await update_statistic('after', time_point_finish)
		await send_request(job_data[0], result, job_data[3])


	records = await get_wait_job()

	coros = [execute_test(records[i]) for i in range(len(records))]
	await asyncio.gather(*coros)


while True:
	time.sleep(0.2)
	loop = asyncio.get_event_loop()
	loop.run_until_complete(main())
	time.sleep(0.2)


cursor.close()
conn.close()