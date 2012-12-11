def convert_flat_dict_to_nested(dictionary):
	"""
	Currently only goes one level deep

	>>> convert_flat_dict_to_nested({"key1[subkey]":"value1","key2":"value2"})
	{"key1":{"subkey":"value1"},"key2":"value2"}

	>>> convert_flat_dict_to_nested({"key[0]":"value0", "key[1]":"value1"})
	{'key': ['value0', 'value1']}
	
	"""
	def key_has_subkeys(key):
		return '[' in key and ']' in key

	def get_top_key(key):
		return key.split('[')[0]

	newDictionary = {}

	sortedItems = dictionary.items()
	sortedItems.sort()
	for key,value in sortedItems:
		if key_has_subkeys(key):
			topKey = get_top_key(key)
			topKeyRemoved = key[len(topKey)+1:].replace(']','',1)
			subKey = get_top_key(topKeyRemoved)

			
			try:
				#check for array values e.g. category[0], throws ValueError if subKey is not an integer
				index = int(subKey)

				#get existing array or blank one if it doesnt exist
				subArray = newDictionary.get(topKey,[])

				if subArray and type(subArray) != list:
					raise Exception("Conflict between {0} key and existing key".format(topKey))

				#not using index because values were presorted to preserve order
				subArray.append(value)
				newDictionary[topKey] = subArray

			except ValueError:
				#continue with dictionary
				#get existing subDictionary or blank one if it doesnt exist
				subDictionary = newDictionary.get(topKey,{})

				#check and make sure we actually got a dict
				if subDictionary and type(subDictionary) != dict:
					raise Exception("Conflict between {0} key and existing key".format(topKey))
				

				#build new subDictionary
				

				subDictionary[subKey] = value

				newDictionary[topKey] = subDictionary
		else:
			newDictionary[key] = value
	return newDictionary

def convert_dict_to_urlencoded_string(dictionary):
	"""
	The purpose of this utility is to convert from a python dictionary to a urlencoded string in the format that sendgrid sends in single event api POSTs
	"""
	def add_keyvalue_to_string(string,keyvalue,separator='&'):
		if len(string) > 0:
			return "{string}{separator}{keyvalue}".format(string=string,keyvalue=keyvalue,separator=separator)
		else:
			return keyvalue

	string = ""
	for key,value in dictionary.items():
		if type(value)==dict:
			for subKey,subValue in value.items():
				if type(subValue)==dict:
					raise NotImplementedError("Sub dictionaries more than 1 level deep are currently not supported")
				keyvalue = "{key}[{sub_key}]={sub_value}".format(key=key,sub_key=subKey,sub_value=subValue)
				string = add_keyvalue_to_string(string,keyvalue)

		elif type(value)==list:
			for i,subValue in enumerate(value):
				keyvalue = "{key}[{i}]={sub_value}".format(key=key,i=i,sub_value=subValue)
				string = add_keyvalue_to_string(string,keyvalue)
		else:
			keyvalue = "{key}={value}".format(key=key,value=value)
			string = add_keyvalue_to_string(string,keyvalue)

	return string

def get_value_from_dict_using_formdata_key(key,dictionary):
	"""
	Example:
	key="newsletter[newsletter_id]"
	dict={"newsletter":{"newsletter_id": 123}}

	returns 123
	"""
	if not dictionary:
		return None
	#check if we need to go deeper
	if '[' in key and ']' in key:
		#get top level key e.g. topKey[nextKey][anotherKey] => topKey
		topKey = key.split('[')[0]
		#remove top level key, e.g. topKey[nextKey][anotherKey] => nextKey[anotherKey]
		topKeyRemoved = key[len(topKey)+1:].replace(']','',1)
		#recurse
		return get_value_from_dict_using_formdata_key(topKeyRemoved,dictionary.get(topKey,None))
	else:
		return dictionary.get(key,None)