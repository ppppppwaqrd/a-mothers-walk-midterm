from pathlib import Path
from PIL import Image

SRC = Path(r"2D-Platformer-Starter-Kit-main/Assets/Generated/Spritesheet")


def neighbors8(x, y, w, h):
	for ny in range(y - 1, y + 2):
		for nx in range(x - 1, x + 2):
			if (nx, ny) != (x, y) and 0 <= nx < w and 0 <= ny < h:
				yield nx, ny


def clean(path: Path):
	im = Image.open(path).convert("RGBA")
	w, h = im.size

	for _pass in range(4):
		px = im.load()
		data = [[px[x, y] for x in range(w)] for y in range(h)]
		for y in range(h):
			for x in range(w):
				r, g, b, a = data[y][x]
				if a == 0:
					continue

				trans = 0
				dark_n = None
				for nx, ny in neighbors8(x, y, w, h):
					rr, gg, bb, aa = data[ny][nx]
					if aa < 20:
						trans += 1
					elif aa > 180 and (rr + gg + bb) < (r + g + b) - 40:
						dark_n = (rr, gg, bb)

				avg = (r + g + b) / 3.0
				chroma = max(r, g, b) - min(r, g, b)

				# orphan crumbs
				if trans >= 7 and avg >= 140:
					px[x, y] = (r, g, b, 0)
					continue

				if trans == 0:
					continue

				# white / pale gray fringe on silhouette
				if avg >= 200:
					px[x, y] = (r, g, b, 0)
					continue
				if avg >= 175 and chroma <= 35:
					px[x, y] = (r, g, b, 0)
					continue
				if avg >= 155 and chroma <= 22 and trans >= 2:
					px[x, y] = (r, g, b, 0)
					continue

				# despill remaining pale edge into darker neighbor / outline
				if avg >= 130 and dark_n is not None:
					t = min(0.85, (avg - 110) / 100.0)
					nr = int(r * (1 - t) + dark_n[0] * t)
					ng = int(g * (1 - t) + dark_n[1] * t)
					nb = int(b * (1 - t) + dark_n[2] * t)
					na = int(a * (1 - 0.25 * t))
					px[x, y] = (nr, ng, nb, max(0, na))
				elif avg >= 160 and chroma <= 40:
					# force dark outline instead of pale fringe
					px[x, y] = (48, 28, 16, min(a, 220))

	# final orphan pass
	px = im.load()
	data = [[px[x, y] for x in range(w)] for y in range(h)]
	for y in range(h):
		for x in range(w):
			r, g, b, a = data[y][x]
			if a == 0:
				continue
			trans = sum(1 for nx, ny in neighbors8(x, y, w, h) if data[ny][nx][3] < 20)
			if trans >= 6:
				px[x, y] = (r, g, b, 0)

	im.save(path)
	opaque = sum(1 for p in im.getdata() if p[3] > 0)
	print(f"{path.name}: opaque={opaque}")


def main():
	for name in [
		"mother_idle.png",
		"mother_walk.png",
		"mother_jump.png",
		"mother_throw.png",
	]:
		clean(SRC / name)


if __name__ == "__main__":
	main()
