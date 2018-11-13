def get_sentences(text, deep=False):

	def _split(array, pattern, add):
		
		def _selective_split(array, pattern, add):
			temp=[]

			for line in array:
				for elem in line.split(pattern):
					if elem and not elem.isspace():
						if elem[-1] in ['.', '?', ',']:
							temp.append(elem)
						else:
							temp.append(elem+add)
			return temp

		print ('1 ')
		print (array)
		array=_selective_split(array, ' '+pattern+' ', add)
		print ('2 ')
		print (array)
		array=_selective_split(array, pattern+' ', add)
		print ('3 ')
		print (array)
		array=_selective_split(array, ' '+pattern, add)
		print ('4 ')
		print (array)
		array=_selective_split(array, pattern, add)
		print ('5 ')
		print (array)

		return array

	array=text.split('. ')
	for elem in array:
		elem += ' .'

	if deep:
		array=_split(array, ',', ' ,')

	array=_split(array, '?', ' ?')
	return array


print(get_sentences('ciao, allora ?wwwee ? dwe? .'))
print('fff')
print(get_sentences('ciao, allora ?wwwee ? dwe? .', True))