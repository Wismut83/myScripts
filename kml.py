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

	def center(self, list_input):
		accu = 3
		x, y, z = 0, 0, 0
		for name in list_input:
			x+=name[0]
			y+=name[1]
			z+=name[2]
		x = round(x/len(list_input),accu)
		y = round(y/len(list_input),accu)
		z = round(z/len(list_input),accu)
		return x,y,z

	def middle(self, list_input):
		length, az = 0, 0
		for list in list_input:
			length += list[3]
			az += list[4]
		length = round(length/len(list_input),3)
		az = round(az/len(list_input),3)
		return length, az

	def area_az_dip(self, list):
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

	def az_from_coords(self, list):
		x1, x2 = list[0][0], list[1][0]
		y1, y2 = list[0][1], list[1][1]

		dx = x1-x2
		dy = y1-y2
		atg = math.degrees(math.atan((y2-y1)/(x2-x1)))
		if dx<0 and dy<0:
			az = 90-atg
		elif dx<0 and dy>0:
			az = 90+atg
		elif dx>0 and dy>0:
			az = 270-atg-180
		elif dx>0 and dy<0:
			az = 270+atg-180
		else:
			print('no one line')
		return az

	def text_coords_to_float(self, coords):
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
		return coords

	def length_from_coords(self, list):
		x = (list[0][0]-list[1][0])*(list[0][0]-list[1][0])
		y = (list[0][1]-list[1][1])*(list[0][1]-list[1][1])
		z = (list[0][2]-list[1][2])*(list[0][2]-list[1][2])
		return math.sqrt(x+y+z)

	def kml_to_list_orientation(self, file, list_out):
		with open(file) as kml:
			data = kml.readlines()
			for idy, line in enumerate(data):
				string = line.split()
				if "<LineString>" in line:
					try:
						if 'true' in data[idy+1]:
							shale = 1
						else:
							shale = 0
						coords = data[idy+3]
						coords = self.text_coords_to_float(coords)
						x, y, z = self.center(coords)
						az, dip, area = self.area_az_dip(coords)
						list_out.append([x,y,z,az,dip, shale, area])
					except:
						print('Probably an empty line: {} ({})'.format(idy, file))

	def kml_to_list_size(self, file, list_out):
		dictionary = {}
		with open(file) as kml:
			data = kml.readlines()
			for idy, line in enumerate(data):
				string = line.split()
				if "<LineString>" in line:
					try:
						name = data[idy-2]
						name = name.replace('      <name>','')
						name = name.replace('</name>\n','')
						coords = data[idy+3]
						coords = self.text_coords_to_float(coords)

						if '<Placemark>' in name:
							dictionary.update({'noname {}'.format(idy):[]})
							for idx in range(0,len(coords)-1):
								list_noname = [coords[idx], coords[idx+1]]
								x, y, z = self.center(list_noname)
								length = self.length_from_coords(list_noname)
								az = self.az_from_coords(list_noname)
								dictionary['noname {}'.format(idy)].append([x, y, z, length, az])
							continue

						x, y, z = self.center(coords)
						length = self.length_from_coords(coords)
						az = self.az_from_coords(coords)
						if dictionary.get(name,0) == 0:
							dictionary.update({name:[]})
						dictionary[name].append([x, y, z, length, az])
					except:
						print('Probably an empty line: {} ({})'.format(idy, file))

		for name in dictionary:
			
			x, y, z = self.center(dictionary[name])
			length, az = self.middle(dictionary[name])
			list_out.append([x,y,z,length, az])
		print('goups:', len(dictionary.keys()))

	def list_to_txt(self, list_input, waytxt):
		coords = open(waytxt, 'a')

		with open(waytxt, "a") as file:
			for line in list_input:
				a = [str(i) for i in line]
				file.write(' '.join(a) + '\n')

	def kml_to_txt_triangle(self, filename=r'\resut_triangle.txt'):
		waytxt = self.way + filename
		with open(waytxt, "w") as file:
			file.write('X Y Z Az Dip Shale Square\n')
		os.chdir(self.way)
		for file in glob.glob("*.kml"):
			list_out = []
			self.kml_to_list_orientation(file,list_out)
			self.list_to_txt(list_out, waytxt)

	def kml_to_txt_line(self, filename=r'\resut_length.txt'):
		waytxt = self.way + filename
		with open(waytxt, "w") as file:
			file.write('X Y Z length az\n')
		os.chdir(self.way)
		for file in glob.glob("*.kml"):
			list_out = []
			self.kml_to_list_size(file, list_out)
			self.list_to_txt(list_out, waytxt)

# a = kml(r"Z:\работы\2019\Олкон\рабочие файлы\2 этап\поиск трещин\Q3")
# a.kml_to_txt_triangle()
a = kml(r'D:\ivan')
a.kml_to_txt_line()
