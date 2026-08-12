from pathlib import Path
from PIL import Image

SRC = Path(r"2D-Platformer-Starter-Kit-main/Assets/Generated/Spritesheet")


def neighbors8(x, y, w, h):
	for ny in range(y - 1, y + 2):
		for nx in range(x - 1, x + 2):
			if (nx, ny) != (x, y) and 0 <= nx < w and 0 <= ny < h:
				yield nx, ny


def harden(path: Path):
	im = Image.open(path).convert("RGBA")
	w, h = im.size
	px = im.load()

	# 1) soft alpha on pale pixels -> kill (causes white halo when composited)
	for y in range(h):
		for x in range(w):
			r, g, b, a = px[x, y]
			if a == 0:
				continue
			avg = (r + g + b) / 3.0
			if a < 230 and avg >= 90:
				px[x, y] = (r, g, b, 0)
			elif 0 < a < 255:
				# keep colored soft pixels as solid
				px[x, y] = (r, g, b, 255)

	# 2) shrink pale silhouette rim
	for _ in range(2):
		data = [[px[x, y] for x in range(w)] for y in range(h)]
		for y in range(h):
			for x in range(w):
				r, g, b, a = data[y][x]
				if a == 0:
					continue
				trans = sum(1 for nx, ny in neighbors8(x, y, w, h) if data[ny][nx][3] == 0)
				if trans == 0:
					continue
				avg = (r + g + b) / 3.0
				chroma = max(r, g, b) - min(r, g, b)
				# pale rim / light gray hair-fringe leftovers
				if avg >= 115 and chroma <= 55:
					px[x, y] = (r, g, b, 0)
				elif avg >= 100 and chroma <= 30 and trans >= 2:
					px[x, y] = (r, g, b, 0)
				elif avg >= 95 and trans >= 3:
					# replace with dark outline instead of bright rim
					px[x, y] = (42, 24, 14, 255)

	# 3) orphans
	data = [[px[x, y] for x in range(w)] for y in range(h)]
	for y in range(h):
		for x in range(w):
			r, g, b, a = data[y][x]
			if a == 0:
				continue
			trans = sum(1 for nx, ny in neighbors8(x, y, w, h) if data[ny][nx][3] == 0)
			if trans >= 6:
				px[x, y] = (r, g, b, 0)

	im.save(path)
	# edge stats
	data = list(im.getdata())
	opaque = sum(1 for p in data if p[3] > 0)
	semi = sum(1 for p in data if 0 < p[3] < 255)
	print(f"{path.name}: opaque={opaque} semi={semi}")


def main():
	for name in [
		"mother_idle.png",
		"mother_walk.png",
		"mother_jump.png",
		"mother_throw.png",
	]:
		harden(SRC / name)


if __name__ == "__main__":
	main()
