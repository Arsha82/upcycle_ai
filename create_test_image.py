from PIL import Image, ImageDraw

def create_test_image():
    img = Image.new('RGB', (300, 300), color = (73, 109, 137))
    d = ImageDraw.Draw(img)
    d.text((10,10), "Test Waste Item: Plastic Bottle", fill=(255,255,0))
    img.save('test_image.jpg')
    print("Created test_image.jpg")

if __name__ == "__main__":
    create_test_image()
