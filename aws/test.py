
import time ,random
from datetime import datetime, timezone

from auth import auth
print(time.time())

print(int(time.mktime(time.strptime('2000-01-01 12:34:00', '%Y-%m-%d %H:%M:%S'))) - time.timezone)

print(time.strftime("%a, %d %b %Y %H:%M:%S +0000", time.localtime()))
print(time.strftime("%Y %m %d %H:%M:%S", time.localtime()))

def a():
	stamp = int(time.time() * 1000)
	smear = int(random.random() * 1E20) % 0x10000000000000000
	return '%016X%016X' % (stamp, smear)


print('%s - %s - %s', a(), a(), a())

print(datetime.now())
d=datetime.now()
print(d.strftime('%Y-%m-%dT%H:%M:%S'))

#2005-08-15T15:52:01+00:00


d=datetime.now()

year=str(d.year)

if d.month < 10:
	month='0'+str(d.month)
else:
	month=str(d.month)

if d.day < 10:
	day='0'+str(d.day)
else:
	day=str(d.day)

bucket='bucket_name'+'/'+'user'+'/'+year+'/'+month+'/'+day+'/'
key=d.strftime('%Y-%m-%dT%H:%M:%S')+'wav'

print(bucket)
print(key)

print(auth('AJarvisApp', 'passwordAjarvis'))
print(auth('AJarvisAppp', 'passwordAjarvis'))
print(auth('AJarvisApp', 'passwordAjarvi'))


print('/'+d.strftime('%Y-%m-%dT%H:%M:%S')+'.wav')
print(key.encode('utf-8'))

print(datetime.now(timezone.utc))