import requests, re, questionary, random
from bs4 import BeautifulSoup
from os import system, path, mkdir, access, R_OK
from glob import glob
from concurrent.futures import ThreadPoolExecutor
from questionary import Validator, ValidationError, prompt
count = None

if not access("/sdcard/", R_OK):
	print(" ! izinkan akses penyimpanan ke termux di pengaturan atau ketik termux-setup-storage di termux")
	system("termux-setup-storage")

exec('if not path.exists("/sdcard/komiku"):\n\tmkdir("/sdcard/komiku")\nif not path.exists("/sdcard/komiku/koleksi"):\n\tmkdir("/sdcard/komiku/koleksi")\nif not path.exists("/data/data/com.termux/files/home/.termux/termux.properties"):\n\ttry:\n\t\ttry:\n\t\t\tmkdir("/data/data/com.termux/files/home/.termux")\n\t\texcept:\n\t\t\tpass\n\t\tkey = "extra-keys = [[\'ESC\',\'/\',\'-\',\'HOME\',\'UP\',\'END\',\'PGUP\'],[\'TAB\',\'CTRL\',\'ALT\',\'LEFT\',\'DOWN\',\'RIGHT\',\'PGDN\']]"\n\t\topen(\'/data/data/com.termux/files/home/.termux/termux.properties\',\'w\').write(key)\n\t\tsystem(\'termux-reload-settings\')\n\texcept:\n\t\tpass')

user_agent = random.SystemRandom().choice(["Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/74.0.3729.157 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 6.0.1; SM-G532G Build/MMB29T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.83 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 6.0; vivo 1713 Build/MRA58K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.124 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 7.0; SM-G570M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.100 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 5.1; A37f Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.93 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 6.0.1; Redmi 4A Build/MMB29M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.116 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 7.0; SM-G570M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.87 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 7.1; vivo 1716 Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.98 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 7.0; SAMSUNG SM-G610M Build/NRD90M) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/7.4 Chrome/59.0.3071.125 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 7.0; TRT-LX2 Build/HUAWEITRT-LX2; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36",
"Mozilla/5.0 (Linux; Android 7.1.2; Redmi 4X Build/N2G47H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.111 Mobile Safari/537.36"])

class Aoa:
	
	def __repr__(self):
		return f"<that: {self.judul}>"
	
	@property
	def json_data(self):
		return self.__dict__

class Komiku(requests.Session):
	
	def __init__(self, url):
		super().__init__()
		self.url = url
		self.headers.update({"user-agent": user_agent})

	@property
	def details(self):
		confused = Aoa()
		res = self.get(self.url)
		parser = BeautifulSoup(res.text, "html.parser")
		informasi = parser.find("section", id="Informasi")
		table = informasi.find("table").find_all("tr")
		genre = informasi.find("ul").find_all("a")
		daftar = parser.find("table", id="Daftar_Chapter").find_all("tr")[1:][::-1]
		judul = parser.find("header", id="Judul").find("h1").text.strip()
		#judul = re.search("Judul\s?.*?td\s.*?>(.*?)<", str(table[0])).group(1)
		jenis = re.search("Jenis\s?.*?<b>(.*?)<", str(table[1])).group(1)
		konsep = re.search("Konsep\s?.*?<td>(.*?)<", str(table[2])).group(1)
		mangaka = re.search("Komikus\s?.*?td\s.*?>(.*?)<", str(table[3])).group(1)
		status = re.search("Status\s?.*?<td>(.*?)<", str(table[4])).group(1)
		genre = ", ".join(x.text for x in genre)
		output = "/sdcard/komiku/koleksi/" + judul
		chapter_list = self.chapter_list(daftar)
		if (sinopsis := re.search("Sinopsis Lengkap\s+</h2>\s+<p>\s+(.*?)</p>", res.text, re.DOTALL)):
			sinopsis = sinopsis.group(1).strip() + "\n"
		if (ringkasan := re.search("Ringkasan\s+</h3>\s+<p>(.*?)</p><p>(.*?)</p><p>(.*?)</p>\s+<h2>", res.text, re.DOTALL)):
			ringkasan = " ".join(ringkasan.groups()) + "\n"
		for x in ["judul", "jenis", "konsep", "mangaka", "status", "genre", "sinopsis", "ringkasan", "chapter_list", "output"]:
			exec(f"confused.{x} = {x}")
		return confused

	def chapter_list(self, list_chapter):
		lol = []
		for x in list_chapter:
			h = x.find("a")
			i = x.find("td", class_="tanggalseries")
			lol.append({"no": h.text.strip(), "date": i.text.strip(), "url": "https://komiku.id" + h["href"]})
		return {"chapter-list": lol}
	
	def ekstrak(self, chapter_url):
		res = self.get(chapter_url)
		parser = BeautifulSoup(res.text, "html.parser")
		gambar = parser.find("section", id="Baca_Komik").find_all("img", alt=True)
		return [x["src"] for x in gambar]
		
class Search(requests.Session):
	
	def __init__(self, search_url):
		super().__init__()
		self.search_url = search_url
		self.headers.update({"user-agent": user_agent})
	
	@property
	def cari(self):
		confused = Aoa()
		res = self.get(self.search_url)
		parser = BeautifulSoup(res.text, "html.parser")
		list = parser.find("div", class_="daftar")
		if re.search("\s+kosong", str(list)):
			exit(f" [!] tidak ditemukan manga/manhwa/manhua dengan judul {query}")
		result_list = self.result_list(list.find_all("div", class_="bge"))
		if (prev := parser.find("a", class_="prev", href=True)):
			prev = "https://data.komiku.id" + prev["href"]
		if (next := parser.find("a", class_="next", href=True)):
			next = "https://data.komiku.id" + next["href"]
		result_list.update({"prev": prev, "next": next})
		confused.judul = len(result_list["result-list"])
		confused.data = result_list
		return confused

	def result_list(self, list_result):
		lol = []
		for x in list_result:
			info = x.find("div", class_="kan")
			title = info.find("h3").text.strip()
			url = info.find("a")["href"]
			lol.append({"title": title, "url": url})
		return {"result-list": lol}
		
#chapter = chapter[int(select[0]) - 1: int(select[1])]
#break

class Validate(Validator):
	def validate(self, document):
		if re.search("\d+\W\d+", document.text) and "-" in document.text:
			select = document.text.split("-")
			if int(select[0]) <= int(select[1]):
				if int(select[0]) <= len(chapter) and int(select[1]) <= len(chapter):
					None
				else:
					raise ValidationError(message=f"! error {select[0] +' dan' if int(select[0]) >= len(chapter) else ''} {select[1]} lebih dari {len(chapter)}", cursor_position=len(document.text))
			else:
				raise ValidationError(message=f"! error [{select[0]}:{select[1]}]", cursor_position=len(document.text))
		else:
			raise ValidationError(message="! isi dengan benar", cursor_position=len(document.text))

def download(url, output, total):
	global count
	if not path.exists(output + "/" + url.split("/")[-1]):
		res = requests.get(url).content
		open(output + "/" + url.split("/")[-1], "wb").write(res)
	count += 1
	print(f"\r [*] downloading {count}/{total}", end="")
	
def dizzy(url: str) -> dict:
	result = Search(url).cari.json_data
	list = [x["title"] for x in result["data"]["result-list"]]
	if result["data"]["prev"]:
		list.append("PREV PAGE")
	if result["data"]["next"]:
		list.append("NEXT PAGE")
	select = questionary.select("select:", choices=list).ask()
	if select in ("PREV PAGE", "NEXT PAGE"):
		return dizzy(result["data"][select.split()[0].lower()])
	select = result["data"]["result-list"][list.index(select)]
	return select

def main(objek: type) -> None:
	system("clear"); print()
	global count, chapter
	details = objek.details
	chapter = details.chapter_list["chapter-list"]
	print("\n".join([f" [*] {x.title()}: {y}" for x, y in details.json_data.items() if x in ["judul", "jenis", "konsep", "mangaka", "status", "genre", "sinopsis"]]))
	print(f"\x1b[0;34m+ \x1b[1;37mtotal chapter: {len(chapter)}\x1b[0m")
	if path.exists(details.output + "/.now"):
		print(f"\x1b[0;34m+ \x1b[1;37mchapter yg sudah diunduh: {open(details.output + '/.now').read().strip()}")
	print("\x1b[0;34m* \x1b[1;37mcontoh: 1-10")
	select = questionary.text("select chapter:", validate=Validate).ask().split("-")
	chapter_ = chapter[int(select[0]) - 1: int(select[1])]
	print()
	if not path.exists(details.output):
		mkdir(details.output)
	for x in chapter_:
		if not path.exists(details.output + "/" + x["no"]):
			mkdir(details.output + "/" + x["no"])
		count = 0
		image = objek.ekstrak(x["url"])
		exists = glob(details.output + "/" + x["no"] + "/*")
		if len(exists) == len(image):
			print(" [!] skip " + details.output + "/" + x["no"] + "\n" * 2)
			continue
		print(f" [*] {details.judul} {x['no']}")
		with ThreadPoolExecutor(max_workers=5) as thread:
			thread.map(lambda _: download(_,  details.output + "/" + x["no"], len(image)), image)
		open(details.output + "/.now", "w").write(x['no'] + " index " + str(chapter.index(x)))
		print("\n" * 2)
		
if __name__ == "__main__":
	#system("clear")
	print("\n\t_  _ ____ _  _ _ _  _ _  _ \n\t|_/  |  | |\/| | |_/  |  | \n\t| \_ |__| |  | | | \_ |__| \n\n    <[ https://github.com/mark-zugbreg ]>\n\n\x1b[0;34m+ \x1b[1;37mcontoh: chainsaw man\x1b[0m")
	query = questionary.text("search:", validate=lambda x: True if x != " "*len(x) else "! don't be empty dude").ask()
	main(Komiku(
		dizzy(f"https://data.komiku.id/cari/?post_type=manga&s={'+'.join(query.split(' '))}")["url"]
	))
	
#print(
#Komiku("https://komiku.id/manga/vinland-saga/").details.json_data
#)
