import math
import glob, os

class kml:
	def __init__(self, way, q, open='non'):
		self.way = way
		self.q = q
		self.errors = 0
		if self.q == 1:
			print('Recalculating by Komsomolsky')
		elif self.q == 2:
			print('Recalculating by Kirovogorsky')
		elif self.q == 3:
			print('Recalculating by Olenegorsky')
		else:
			print('Error in pit selection')
		self.open = open

	def code(self, list):
		if self.q == 1:
			a = (list[0] - 33.16402807) * 41770.9055
			b = (list[1] - 68.1607631) * 111211.8087
		elif self.q == 2:
			a = (list[0] - 33.16402826) * 41506.1997
			b = (list[1] - 68.16016716) * 112103.652
		elif self.q == 3:
			a = (list[0] - 33.16402826) * 41506.1997
			b = (list[1] - 68.16016716) * 112103.652

		c = list[2] + 22 - 300.0
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
		length, az, dip = 0, 0, 0
		for list in list_input:
			length += list[3]
			az += list[4]
			dip += list[5]
		length = round(length/len(list_input),3)
		az = round(az/len(list_input),3)
		dip = round(dip/len(list_input),3)
		return length, az, dip

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
		if list[0][2]>list[1][2]:
			x1, x2 = list[0][0], list[1][0]
			y1, y2 = list[0][1], list[1][1]
			dz = list[0][2]-list[1][2]
		else:
			x2, x1 = list[0][0], list[1][0]
			y2, y1 = list[0][1], list[1][1]
			dz =  list[1][2]-list[0][2]

		dx = x1-x2
		dy = y1-y2

		atg = math.degrees(math.atan(abs(dy)/abs(dx)))
		if dx<0 and dy<0:
			az = 180+atg
		elif dx<0 and dy>0:
			az = 180-atg
		elif dx>0 and dy>0:
			az = atg
		elif dx>0 and dy<0:
			az = 360-atg
		else:
			print('no one line')

		l = math.sqrt((x1-x2)**2+(y1-y2)**2)
		dip = math.degrees(math.atan(l/dz))

		return round(az,1), round(dip,1)

	def gist_tr(self, list_input, filename=r'\3d_table.txt'):
		list_file = []
		step_az = 10
		step_dip = 10
		for dip in range(0,90,step_dip):
			for az in range(0,360,step_az):
				n = 0
				for list in list_input:
					if az<list[3] and az+step_az>=list[3] and dip<list[4] and dip+step_dip>=list[4]:
						n += 1

				list_file.append([dip+step_dip/2,az+step_az/2,n])
		waytxt = self.way + filename
		with open(waytxt, "w") as file:
			file.write('Dip Az N\n')
		self.list_to_txt(list_file, waytxt)
		if self.open == 'open':
			os.startfile(waytxt)

	def gist_ln(self, list_input, filename=r'\3d_table.txt'):
		list_file = []
		step_az = 10
		step_dip = 10
		for dip in range(0,90,step_dip):
			for az in range(0,360,step_az):
				n = 0
				l = 0
				for list in list_input:
					if az<list[3] and az+step_az>=list[3] and dip<list[4] and dip+step_dip>=list[4]:
						n += 1
						l += list[5]

				list_file.append([dip+step_dip/2,az+step_az/2,n, l])

		waytxt = self.way + filename
		with open(waytxt, "w") as file:
			file.write('Dip Az N, L\n')
		self.list_to_txt(list_file, waytxt)
		if self.open == 'open':
			os.startfile(waytxt)

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
		return round(math.sqrt(x+y+z),3)

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
						self.errors+=1
						print('Probably an empty line: {} ({})'.format(idy, file))

	def kml_to_list_size(self, file, list_out):
		with open(file) as kml:
			data = kml.readlines()
			for idy, line in enumerate(data):
				string = line.split()
				if "<LineString>" in line:
					try:
						coords = data[idy+3]
						coords = self.text_coords_to_float(coords)

						for idx in range(0,len(coords)-1):
							co_list = [coords[idx], coords[idx+1]]
							x, y, z = self.center(co_list)
							length = self.length_from_coords(co_list)
							az, dip = self.az_from_coords(co_list)
							list_out.append([x, y, z, az, dip, length])
					except:
						self.errors+=1
						print('Probably an empty line: {} ({})'.format(idy, file))

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
		c = 0
		os.chdir(self.way)
		all_points = []
		for file in glob.glob("*.kml"):
			c+=1
			list_out = []
			self.kml_to_list_orientation(file,list_out)
			for line in list_out:
				all_points.append(line)
			self.list_to_txt(list_out, waytxt)
		self.gist_tr(all_points)
		print('Read {} files. There are {} errors. End of calculation\n'.format(c, self.errors))
		if self.open == 'open':
			os.startfile(waytxt)

	def kml_to_txt_line(self, filename=r'\resut_length.txt'):
		waytxt = self.way + filename
		with open(waytxt, "w") as file:
			file.write('X Y Z Az Dip length\n')
		os.chdir(self.way)
		c = 0
		all_points = []
		for file in glob.glob("*.kml"):
			c += 1
			list_out = []
			self.kml_to_list_size(file, list_out)
			for line in list_out:
				all_points.append(line)
			self.list_to_txt(list_out, waytxt)
		self.gist_ln(all_points)	
		print('Read {} files. There are {} errors. End of calculation\n'.format(c, self.errors))
		if self.open == 'open':
			os.startfile(waytxt)

c = 3

a = kml(r"Z:\работы\2019\Олкон\рабочие файлы\2 этап\поиск трещин\Q{}\triangle".format(c),c)

a.kml_to_txt_triangle()



b = kml(r"Z:\работы\2019\Олкон\рабочие файлы\2 этап\поиск трещин\Q{}\length".format(c),c)

b.kml_to_txt_line()


