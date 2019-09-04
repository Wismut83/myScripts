import math
import glob, os

class kml:
	def __init__(self, way):
		self.way = way

	def code(self, list):
		a = (list[0] - 33.16310263) * 41680.84709
		b = (list[1] - 68.16161113) * 110042.9003
		c = list[2] + 21.7455 - 300.0
		return [a,b,c]

	def centr(self, list_input):
		accu = 3
		x, y, z = 0, 0, 0
		for idx in range(0,len(list_input)):
			x+=list_input[idx][0]
			y+=list_input[idx][1]
			z+=list_input[idx][2]
		x = round(x/len(list_input),accu)
		y = round(y/len(list_input),accu)
		z = round(z/len(list_input),accu)
		print(x,y,z)
		return x,y,z


	# def centr(self, list):
	# 	print(list)
	# 	accu = 3
	# 	x = round((list[0][0]+list[1][0]+list[2][0])/3,accu)
	# 	y = round((list[0][1]+list[1][1]+list[2][1])/3,accu)
	# 	z = round((list[0][2]+list[1][2]+list[2][2])/3,accu)
	# 	return [x,y,z]

	def areaAzDip(self, list):
		a, b = [], []
		for idx in range(0,3):
			a.append(list[1][idx]-list[0][idx])
			b.append(list[2][idx]-list[0][idx])
		ab = [a[1] * b[2] - b[1] * a[2], -(a[0] * b[2] - b[0] * a[2]), a[0] * b[1] - b[0] * a[1]]
		if ab[2]<0:
			for x in range(0, len(ab)):
				ab[x] *= -1
		if ab[0]>0 and ab[1]>0:
			az = math.atan(ab[0] / ab[1])/math.pi * 180
		elif ab[0]<0 and ab[1]>0:
			az = 360 + math.atan(ab[0] / ab[1])/math.pi * 180
		else:
			az = 180 + math.atan(ab[0] / ab[1])/math.pi * 180
		area = math.sqrt(ab[0] * ab[0] + ab[1] * ab[1] + ab[2] * ab[2])/2
		dip = math.asin(math.sqrt(ab[0] * ab[0] + ab[1] * ab[1])/(area*2))/math.pi * 180
		accu = 3
		return round(az,1), round(dip,1), round(area,accu)

	def kml_to_list_orientation(self, file, listout):
		with open(file) as kml:
			data = kml.readlines()
			for idx, line in enumerate(data):
				string = line.split()
				if "<LineString>" in line:
					try:
						if 'true' in data[idx+1]:
							shale = 1
						else:
							shale = 0
						coords = data[idx+3]
						coords = coords.replace('        <coordinates>','')
						coords = coords.replace('</coordinates>\n','')
						coords = coords.split(' ')
						for idx in range(0,len(coords)):
							coords[idx] = coords[idx].split(',')
						for point in coords:
							for idx in range(0,len(point)):
								point[idx] = float(point[idx])
						for idx in range(0,len(coords)):
							coords[idx] = self.code(coords[idx])
						x, y, z = self.centr(coords)
						az, dip, area = self.areaAzDip(coords)
						listout.append([x,y,z,az,dip, shale, area])
					except:
						pass

	def kml_to_list_size(self, file, listout):
		with open(file) as kml:
			data = kml.readlines()
			for idx, line in enumerate(data):
				string = line.split()
				if "<LineString>" in line:
					try:
						coords = data[idx+3]
						coords = coords.replace('        <coordinates>','')
						coords = coords.replace('</coordinates>\n','')
						coords = coords.split(' ')
						for idx in range(0,len(coords)):
							coords[idx] = coords[idx].split(',')
						for point in coords:
							for idx in range(0,len(point)):
								point[idx] = float(point[idx])
						for idx in range(0,len(coords)):
							coords[idx] = self.code(coords[idx])

					except:
						pass
		print('затычка')

	def list_to_txt(self, listinput, waytxt):
		coords = open(waytxt, 'a')

		with open(waytxt, "a") as file:
			for line in listinput:
				a = [str(i) for i in line]
				file.write(' '.join(a) + '\n')

	def kml_to_txt(self, type='orientation', filename=r'\resutByPy.txt'):
		waytxt = self.way + filename
		with open(waytxt, "w") as file:
			file.write('X Y Z Az Dip Shale Square\n')
		os.chdir(self.way)
		for file in glob.glob("*.kml"):
			listout = []
			if type == 'orientation':
				self.kml_to_list_orientation(file,listout)
			elif type == 'size':
				self.kml_to_list_size(file, listout)
			self.list_to_txt(listout, waytxt)

a = kml(r"Z:\работы\2019\Олкон\рабочие файлы\2 этап\поиск трещин\Q3")
a.kml_to_txt()