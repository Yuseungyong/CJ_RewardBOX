import board
import neopixel
pixels = neopixel.NeoPixel(board.D18, 8)
pixels[0] = (255, 0, 0)
#pixels.fill((0, 255, 0))