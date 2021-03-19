import requests
import json

# url = 'http://127.0.0.1:5000/send_file/' # localhost basic path // docker isolated container path
# url = 'http://127.0.0.1:5550/send_file/' # localhost docker-compose path
# url = 'http://54.146.212.26:80/send_file/' # EC2 AWS Linux path
# url = 'http://54.162.203.46:80/send_file/'  # EC2 Ubuntu path
url = 'http://fil_rouge_v0.3.rkr.p2021.ajoga.fr/send_file/'
# swagger url: http://fil_rouge_v0.3.rkr.p2021.ajoga.fr/swagger/

my_jpg_fail_img = {'file': open('test1_size_too_big.jpg', 'rb')}
my_jpg_ok_img = {'file': open('test2_size_ok.jpg', 'rb')}
my_png_img = {'file': open('test.png', 'rb')}
my_gif_img = {'file': open('test.gif', 'rb')}
my_txt_file = {'file': open('test.txt', 'rb')}
my_csv_file = {'file': open('test.csv', 'rb')}
my_pdf_file = {'file': open('test.pdf', 'rb')}
not_allowed_file = {'file': open('test.xyz', 'rb')}

# todo: abort if not recognised filetipe

# POST AN IMAGE TO THE SERVER
#print("jpg test image: Image too large (max 200 kb) expect error code 413")
#print("this size filter is handled by docker-compose, and not the API")
#r = requests.post(url, files=my_jpg_fail_img)
#print(r)

#print("jpg working test image")
#r = requests.post(url, files=my_jpg_ok_img)
#print(r.json())

#print("\npng test image:")
#r = requests.post(url, files=my_png_img)
#print((r.json()))

#print("\ngif test image:")
#r = requests.post(url, files=my_gif_img)
#print((r.json()))

# print("\ntest invalid file type:")
# r = requests.post(url, files=not_allowed_file)
#print((r.json()))

# print("\ntest un-formatted text file:")
# r = requests.post(url, files=my_txt_file)
# print(r.json())

#print("\ntest csv:")
#r = requests.post(url, files=my_csv_file)
#print(r.json())

#print("\ntest pdf:")
#r = requests.post(url, files=my_pdf_file)
#print(r.json())

