#!/usr/bin/env python3

import os, json, zipfile

file="config_zip.json"

def zipdir(path, ziph):
	abs_path = os.path.abspath(path)

	for root, dirs, files in os.walk(path):
		for file in files:

			absname = os.path.abspath(os.path.join(root, file))
			arcname = absname[len(abs_path)-len(elem):]
			print('adding %s as %s' % (os.path.join(root, file), arcname))

			ziph.write(absname, arcname)

if __name__ == '__main__':

	with open(file, 'r') as file:
		config=json.load(file)

	zipf=zipfile.ZipFile('lambda.zip', 'w', zipfile.ZIP_DEFLATED)

	#single files
	for elem in config['include']:
		zipf.write(elem)

	#dir
	for elem in config['include_dir']:
		zipdir(elem, zipf)

	#module_dir
	for elem in config['include_module_dir']:
		zipdir(config['path_module_dir']+elem, zipf)

	zipf.close()




